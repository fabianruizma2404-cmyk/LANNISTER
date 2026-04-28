from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd
import requests
import os
import math
import time
import json as json_lib
import re
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# ── Google Gemini ──
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
gemini = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=genai.GenerationConfig(
        temperature=0.4,
        max_output_tokens=8192,
    )
)

# ── Supabase fix ──
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

@app.before_request
def crear_tablas():
    db.create_all()

ORIGEN = {"lat": 7.119349, "lon": -73.122741}

# ── Modelo Usuario ──
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(150), nullable=True)
    empresa = db.Column(db.String(150), nullable=True)
    sector = db.Column(db.String(100), nullable=True)

# ── Traducción ──
def traducir(texto, idioma):
    try:
        res = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": texto, "langpair": f"es|{idioma}"},
            timeout=6
        )
        if res.status_code == 200:
            data = res.json()
            traducido = data.get("responseData", {}).get("translatedMemory", "")
            if traducido and traducido.lower() != texto.lower():
                return traducido
        return texto
    except:
        return texto

# ── Capital del país ──
def obtener_capital(pais):
    try:
        res = requests.get(
            f"https://restcountries.com/v3.1/name/{pais}",
            timeout=5
        )
        data = res.json()
        if isinstance(data, list) and "capital" in data[0]:
            return data[0]["capital"][0]
        return pais
    except Exception as e:
        raise Exception(f"Error capital {pais}: {str(e)}")

# ── Geocoding ──
def geocode(ciudad):
    try:
        key = os.environ.get("OPENCAGE_KEY")
        if not key:
            raise Exception("Falta API KEY OpenCage")
        res = requests.get(
            f"https://api.opencagedata.com/geocode/v1/json?q={ciudad}&key={key}",
            timeout=5
        )
        data = res.json()
        if not data["results"]:
            raise Exception("Sin resultados")
        return data["results"][0]["geometry"]
    except Exception as e:
        raise Exception(f"Error geocode {ciudad}: {str(e)}")

# ── Distancia Haversine ──
def distancia(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ── Cálculo de envío ──
def calcular_envio(ciudad, pais, peso, largo, ancho, alto):
    coords = geocode(f"{ciudad}, {pais}")
    peso_vol = (largo * ancho * alto) / 5000
    peso_final = max(peso, peso_vol)
    dist = distancia(ORIGEN["lat"], ORIGEN["lon"], coords["lat"], coords["lng"])
    costo = 25 + peso_final * 6 + dist * 0.015
    if dist > 3000:
        costo *= 1.2
    return {
        "ciudad": ciudad,
        "pais": pais,
        "lat": coords["lat"],
        "lng": coords["lng"],
        "distancia": int(dist),
        "peso": round(peso_final, 2),
        "costo": round(costo, 2)
    }

# ── Pytrends ──
def get_pytrends():
    return TrendReq(
        hl='es',
        tz=360,
        timeout=(10, 30),
        retries=3,
        backoff_factor=0.5
    )

def top_paises_multilingue(producto):
    idiomas = ["en", "de", "fr", "pt"]
    traducciones = []
    for lang in idiomas:
        t = traducir(producto, lang)
        if t and t.lower() != producto.lower():
            traducciones.append(t)

    keywords_candidatas = list(dict.fromkeys([producto] + traducciones))
    print(f"[Trends] Keywords: {keywords_candidatas}")

    resultados = pd.DataFrame()

    for idx, palabra in enumerate(keywords_candidatas):
        if idx > 0:
            time.sleep(2)
        intentos = 0
        while intentos < 3:
            try:
                pt = get_pytrends()
                pt.build_payload([palabra], timeframe='today 12-m', geo='')
                time.sleep(1.5)
                df = pt.interest_by_region(
                    resolution='COUNTRY',
                    inc_low_vol=True,
                    inc_geo_code=False
                )
                if df is None or df.empty:
                    break
                df = df[(df > 0).any(axis=1)]
                if df.empty:
                    break
                print(f"[Trends] OK '{palabra}': {len(df)} países")
                if resultados.empty:
                    resultados = df.copy()
                else:
                    resultados = resultados.join(df, how="outer", rsuffix=f"_{idx}")
                break
            except Exception as e:
                intentos += 1
                print(f"[Trends] Error intento {intentos} para '{palabra}': {str(e)}")
                time.sleep(3 * intentos)

    if resultados.empty:
        raise Exception("Google Trends sin datos")

    resultados["Promedio"] = resultados.mean(axis=1, skipna=True)
    resultados = resultados.sort_values(by="Promedio", ascending=False)
    resultados = resultados[resultados["Promedio"] > 0]
    top5 = resultados.head(5).index.tolist()
    print(f"[Trends] Top países: {top5}")

    if len(top5) < 3:
        raise Exception(f"Solo {len(top5)} países con datos, se necesitan al menos 3")

    return top5[:3]

# ── REGISTER ──
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Faltan datos"}), 400
    if Usuario.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Usuario ya existe"}), 400
    hashed = generate_password_hash(data["password"])
    user = Usuario(
        email=data["email"],
        password=hashed,
        nombre=data.get("nombre"),
        empresa=data.get("empresa"),
        sector=data.get("sector"),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Usuario creado"})

# ── LOGIN ──
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Datos incompletos"}), 400
    user = Usuario.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Credenciales inválidas"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token})

# ── COTIZADOR ──
@app.route("/cotizar")
@jwt_required()
def cotizar():
    try:
        producto = request.args.get("producto")
        if not producto:
            return jsonify({"error": "Debes ingresar un producto"}), 400
        peso  = float(request.args.get("peso", 3))
        largo = float(request.args.get("largo", 30))
        ancho = float(request.args.get("ancho", 30))
        alto  = float(request.args.get("alto", 30))
        paises = top_paises_multilingue(producto)
        resultados = []
        for pais in paises:
            capital = obtener_capital(pais)
            envio = calcular_envio(capital, pais, peso, largo, ancho, alto)
            resultados.append(envio)
        return jsonify({"resultados": resultados})
    except Exception as e:
        print("ERROR /cotizar:", str(e))
        return jsonify({"error": str(e)}), 500

# ── ANALIZAR (Google Gemini) ──
@app.route("/analizar", methods=["POST"])
@jwt_required()
def analizar():
    respuesta_raw = ""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Datos requeridos"}), 400

        producto = data.get("producto")
        mercados = data.get("mercados")

        if not producto or not mercados:
            return jsonify({"error": "Faltan producto o mercados"}), 400

        # Construir contexto detallado de cada mercado
        mercados_info = []
        for i, m in enumerate(mercados):
            mercados_info.append(
                f"Mercado {i+1}: {m['pais']} | Ciudad: {m['ciudad']} | "
                f"Distancia: {m['distancia']} km desde Bucaramanga | "
                f"Costo logístico: ${m['costo']} USD | Peso: {m['peso']} kg"
            )
        mercados_texto = "\n".join(mercados_info)

        # Construir la estructura JSON esperada con instrucciones específicas por mercado
        instrucciones_por_mercado = []
        for i, m in enumerate(mercados):
            pais = m["pais"]
            ciudad = m["ciudad"]
            costo = m["costo"]
            instrucciones_por_mercado.append(f"""
    {{
      "pais": "{pais}",
      "ciudad": "{ciudad}",
      "analisis": {{
        "precio_referencia": "COMPLETA CON DATOS REALES: rango de precios de '{producto}' en {pais} (precio retail en USD, precio mayorista en USD, precio en moneda local). Calcula si el costo logístico de ${costo} USD es viable según el margen esperado y el volumen mínimo de exportación rentable.",
        "aranceles_y_tratados": "COMPLETA CON DATOS REALES: arancel de importación exacto (%) para '{producto}' en {pais}, partida arancelaria del Sistema Armonizado (SA), si Colombia tiene TLC o SGP con {pais} (nombre del acuerdo y beneficio arancelario concreto), IVA a importaciones y otros impuestos aplicables en {pais}.",
        "incoterms_recomendados": "COMPLETA CON DATOS REALES: Incoterm(s) más convenientes para exportar '{producto}' desde Bucaramanga a {ciudad} — explica por qué (responsabilidades del exportador, distribución de costos y riesgos, tipo de seguro recomendado para esta ruta específica de {m['distancia']} km).",
        "canales_y_compradores": "COMPLETA CON DATOS REALES: canales de distribución específicos en {pais} para '{producto}' — importadores mayoristas, plataformas de e-commerce locales con nombre, ferias del sector en {pais} con nombre y fecha aproximada, estrategia de prospección B2B y plataformas para encontrar compradores (Europages, Trademap, etc.).",
        "requisitos_y_certificaciones": "COMPLETA CON DATOS REALES: certificaciones obligatorias para importar '{producto}' en {pais} (nombre de la entidad reguladora, norma técnica aplicable), idioma y requisitos mínimos del etiquetado, documentos aduaneros requeridos (factura comercial, certificado de origen Form A o de TLC, packing list, BL/AWB), y si el certificado de origen colombiano da beneficio arancelario en {pais}.",
        "estrategia_entrada": "COMPLETA CON DATOS REALES: plan de 3 pasos concretos para entrar al mercado de {pais} con '{producto}' en los próximos 6 meses — paso 1 (mes 1-2), paso 2 (mes 3-4), paso 3 (mes 5-6). Incluye: presupuesto orientativo inicial, forma de pago recomendada (carta de crédito, pago anticipado, etc.), consideraciones culturales de negociación específicas de {pais}, y contactos clave (cámaras de comercio, ProColombia, etc.)."
      }}
    }}{"," if i < len(mercados) - 1 else ""}""")

        estructura = "\n".join(instrucciones_por_mercado)

        prompt = f"""Eres un consultor senior de comercio exterior colombiano con 20 años de experiencia real. Trabajas con ProColombia, conoces los TLC de Colombia en detalle, manejas aranceles del Sistema Armonizado, incoterms 2020 y tienes contacto directo con importadores internacionales.

CONTEXTO DEL ANÁLISIS:
- Producto: "{producto}" — exportado desde Bucaramanga, Santander, Colombia
- Mercados objetivo identificados por análisis de tendencias globales:
{mercados_texto}

INSTRUCCIÓN CRÍTICA:
Debes completar cada campo del JSON con información REAL, ESPECÍFICA y DIFERENTE para cada país. Está PROHIBIDO:
- Dar respuestas genéricas o repetir la misma información en distintos mercados
- Omitir rangos de precios numéricos en USD
- Inventar datos — usa tu conocimiento real de comercio exterior
- Agregar texto fuera del JSON

Cada análisis debe reflejar las particularidades reales de ese país: su régimen arancelario, sus canales de distribución propios, sus normas técnicas específicas y su cultura de negocios.

Responde ÚNICAMENTE con este JSON completamente relleno con datos reales (reemplaza las instrucciones por el contenido real):

{{
  "mercados": [{estructura}
  ]
}}"""

        print(f"[Gemini] Enviando prompt para: {producto} en {len(mercados)} mercados")

        response = gemini.generate_content(prompt)
        respuesta_raw = response.text.strip()

        print(f"[Gemini] Respuesta recibida ({len(respuesta_raw)} chars)")

        # Limpieza robusta de markdown
        if "```" in respuesta_raw:
            match = re.search(r'```(?:json)?\s*([\s\S]*?)```', respuesta_raw)
            if match:
                respuesta_raw = match.group(1).strip()
            else:
                respuesta_raw = respuesta_raw.replace("```json", "").replace("```", "").strip()

        # Extraer solo el JSON
        primer_llave = respuesta_raw.find("{")
        if primer_llave > 0:
            respuesta_raw = respuesta_raw[primer_llave:]

        ultima_llave = respuesta_raw.rfind("}")
        if ultima_llave != -1 and ultima_llave < len(respuesta_raw) - 1:
            respuesta_raw = respuesta_raw[:ultima_llave + 1]

        respuesta_raw = respuesta_raw.strip()

        analisis_json = json_lib.loads(respuesta_raw)

        return jsonify({"analisis": analisis_json})

    except json_lib.JSONDecodeError as e:
        print("ERROR JSON /analizar:", str(e))
        print("Raw (primeros 600):", respuesta_raw[:600])
        return jsonify({"error": "El modelo no devolvió JSON válido. Intenta de nuevo."}), 500

    except Exception as e:
        print("ERROR /analizar:", str(e))
        return jsonify({"error": "Error al generar el análisis. Intenta de nuevo."}), 500

# ── RUN ──
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
