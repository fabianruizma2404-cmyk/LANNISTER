from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd
import requests
import os
import math
import time
import json as json_lib
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from groq import Groq

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🔥 FIX SUPABASE
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# 🔥 CREAR DB AUTOMÁTICAMENTE
@app.before_request
def crear_tablas():
    db.create_all()

# 📍 Origen
ORIGEN = {"lat": 7.119349, "lon": -73.122741}

# 👤 Modelo Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(150), nullable=True)
    empresa = db.Column(db.String(150), nullable=True)
    sector = db.Column(db.String(100), nullable=True)

# 🌍 Traducción — usando MyMemory (gratuito, sin servidor caído)
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

# 🌎 Obtener capital
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

# 📍 Geocode
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

# 📏 Distancia
def distancia(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# 💰 Envío
def calcular_envio(ciudad, pais, peso, largo, ancho, alto):
    coords = geocode(f"{ciudad}, {pais}")

    peso_vol = (largo * ancho * alto) / 5000
    peso_final = max(peso, peso_vol)

    dist = distancia(
        ORIGEN["lat"], ORIGEN["lon"],
        coords["lat"], coords["lng"]
    )

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

# 🧠 Crear instancia fresca de pytrends por request (evita estado corrupto)
def get_pytrends():
    return TrendReq(
        hl='es',
        tz=360,
        timeout=(10, 30),
        retries=3,
        backoff_factor=0.5
    )

# 🧠 Trends — robusto con reintentos y fallback
def top_paises_multilingue(producto):
    # Traducir a varios idiomas para ampliar cobertura
    idiomas = ["en", "de", "fr", "pt"]
    traducciones = []
    for lang in idiomas:
        t = traducir(producto, lang)
        if t and t.lower() != producto.lower():
            traducciones.append(t)

    # Siempre incluir el término original en español
    keywords_candidatas = list(dict.fromkeys([producto] + traducciones))

    print(f"[Trends] Keywords a consultar: {keywords_candidatas}")

    resultados = pd.DataFrame()

    for idx, palabra in enumerate(keywords_candidatas):
        # Pausa entre requests para evitar rate limiting de Google
        if idx > 0:
            time.sleep(2)

        intentos = 0
        while intentos < 3:
            try:
                pt = get_pytrends()
                pt.build_payload(
                    [palabra],
                    timeframe='today 12-m',
                    geo=''
                )

                time.sleep(1.5)

                df = pt.interest_by_region(
                    resolution='COUNTRY',
                    inc_low_vol=True,
                    inc_geo_code=False
                )

                if df is None or df.empty:
                    print(f"[Trends] Sin datos para: {palabra}")
                    break

                # Filtrar filas con valor 0 en todas las columnas
                df = df[(df > 0).any(axis=1)]

                if df.empty:
                    print(f"[Trends] Solo ceros para: {palabra}")
                    break

                print(f"[Trends] OK para '{palabra}': {len(df)} países")

                if resultados.empty:
                    resultados = df.copy()
                else:
                    # join outer y renombrar para evitar colisiones
                    resultados = resultados.join(df, how="outer", rsuffix=f"_{idx}")

                break  # éxito, salir del while

            except Exception as e:
                intentos += 1
                print(f"[Trends] Error intento {intentos} para '{palabra}': {str(e)}")
                time.sleep(3 * intentos)

    if resultados.empty:
        raise Exception("Google Trends sin datos para ninguna keyword")

    # Calcular promedio ignorando NaN
    resultados["Promedio"] = resultados.mean(axis=1, skipna=True)
    resultados = resultados.sort_values(by="Promedio", ascending=False)

    # Filtrar países con promedio > 0
    resultados = resultados[resultados["Promedio"] > 0]

    top5 = resultados.head(5).index.tolist()
    print(f"[Trends] Top países: {top5}")

    if len(top5) < 3:
        raise Exception(f"Solo se encontraron {len(top5)} países con datos, se necesitan al menos 3")

    return top5[:3]

# 📝 REGISTER
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

# 🔐 LOGIN
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

# 📦 COTIZADOR
@app.route("/cotizar")
@jwt_required()
def cotizar():
    try:
        producto = request.args.get("producto")

        if not producto:
            return jsonify({"error": "Debes ingresar un producto"}), 400

        peso = float(request.args.get("peso", 3))
        largo = float(request.args.get("largo", 30))
        ancho = float(request.args.get("ancho", 30))
        alto = float(request.args.get("alto", 30))

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

# 🚀 ANALIZAR
@app.route("/analizar", methods=["POST"])
@jwt_required()
def analizar():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "Datos requeridos"}), 400

        producto = data.get("producto")
        mercados = data.get("mercados")

        if not producto or not mercados:
            return jsonify({"error": "Faltan producto o mercados"}), 400

        # Construir texto detallado de cada mercado
        mercados_texto = ""
        for i, m in enumerate(mercados):
            mercados_texto += (
                f"\n  - Mercado {i+1}: {m['pais']} | Ciudad: {m['ciudad']} | "
                f"Distancia desde Bucaramanga: {m['distancia']} km | "
                f"Costo logístico estimado: ${m['costo']} USD | "
                f"Peso del envío: {m['peso']} kg"
            )

        # Construir lista de mercados para el JSON de salida
        estructura_mercados = ""
        for i, m in enumerate(mercados):
            estructura_mercados += f"""
    {{
      "pais": "{m['pais']}",
      "ciudad": "{m['ciudad']}",
      "analisis": {{
        "precios": "Indica el rango de precios REAL de '{producto}' en {m['pais']}: precio mínimo, precio promedio y precio premium en USD y en la moneda local. Menciona si hay diferencias de precio por canal (retail vs B2B vs online). Da ejemplos de precios reales que un importador en {m['ciudad']} pagaría.",
        "aranceles_y_tratados": "Indica el arancel de importación exacto (%) aplicado a '{producto}' en {m['pais']}, partida arancelaria aproximada, si Colombia tiene TLC o acuerdo vigente con ese país y qué beneficio arancelario concreto implica, e impuestos adicionales (IVA, consumo, etc.).",
        "incoterms_recomendados": "Recomienda los Incoterms más convenientes para exportar '{producto}' desde Bucaramanga hacia {m['ciudad']}, explicando por qué y qué responsabilidades asume el exportador colombiano en cada uno.",
        "canales_y_compradores": "Describe los canales de distribución reales en {m['pais']} para '{producto}': importadores mayoristas, plataformas online locales, ferias del sector, cadenas de retail, brokers. Menciona nombres de empresas o plataformas reales si aplica.",
        "requisitos_y_certificaciones": "Lista los requisitos técnicos, sanitarios, de etiquetado y certificaciones obligatorias para ingresar '{producto}' a {m['pais']}: normas técnicas, entidades reguladoras, idioma del etiquetado, permisos de importación.",
        "estrategia_entrada": "Plan concreto de 3 pasos para entrar al mercado de {m['pais']} con '{producto}' desde Bucaramanga: qué hacer primero, contactos clave, plazos estimados y presupuesto inicial orientativo."
      }}
    }}{"," if i < len(mercados) - 1 else ""}"""

        prompt = f"""Eres un consultor senior de comercio exterior con 20 años de experiencia real asesorando PYMEs colombianas en exportación. Tienes conocimiento profundo y ESPECÍFICO de aranceles internacionales, acuerdos TLC de Colombia, incoterms, operadores logísticos y precios de mercado reales en distintos países.

CONTEXTO DEL CLIENTE:
- Producto a exportar: "{producto}"
- Ciudad de origen: Bucaramanga, Santander, Colombia
- Mercados objetivo identificados por tendencias de Google:{mercados_texto}

TU TAREA: Generar un análisis de exportación DETALLADO, ESPECÍFICO y DIFERENTE para CADA UNO de los {len(mercados)} mercados. NO puedes dar respuestas genéricas. Cada mercado tiene su propio contexto arancelario, precios reales, canales y requisitos.

REGLAS ESTRICTAS:
1. En "precios": SIEMPRE incluir rangos numéricos reales en USD (ej: "$8 - $15 USD por unidad en retail", "$5 - $9 USD precio mayorista"). NO omitas nunca los precios.
2. En "aranceles_y_tratados": incluir el porcentaje exacto de arancel y el nombre del acuerdo comercial si existe.
3. Cada campo debe tener mínimo 3 oraciones con información concreta y diferente entre mercados.
4. Responde ÚNICAMENTE con JSON puro válido, sin texto adicional, sin markdown, sin bloques de código.

JSON requerido (completa los campos con información real, no los dejes como instrucciones):
{{
  "mercados": [{estructura_mercados}
  ]
}}"""

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en comercio exterior colombiano. "
                        "Conoces en detalle los TLC de Colombia, aranceles de importación por país, "
                        "incoterms, precios de mercado internacionales y canales de distribución B2B. "
                        "SIEMPRE respondes con JSON puro válido, sin markdown, sin texto extra. "
                        "NUNCA omites el campo de precios: siempre incluyes rangos numéricos reales en USD. "
                        "Cada mercado tiene análisis completamente distinto y específico."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.75,
            max_tokens=8000,
        )

        respuesta_raw = completion.choices[0].message.content.strip()

        # 🔥 Limpieza robusta de markdown (múltiples casos)
        # Caso: ```json ... ```
        if "```" in respuesta_raw:
            # Extraer contenido entre los backticks
            import re
            match = re.search(r'```(?:json)?\s*([\s\S]*?)```', respuesta_raw)
            if match:
                respuesta_raw = match.group(1).strip()
            else:
                # Fallback: quitar todos los backticks
                respuesta_raw = respuesta_raw.replace("```json", "").replace("```", "").strip()

        # Caso: texto antes del primer {
        primer_llave = respuesta_raw.find("{")
        if primer_llave > 0:
            respuesta_raw = respuesta_raw[primer_llave:]

        # Caso: texto después del último }
        ultima_llave = respuesta_raw.rfind("}")
        if ultima_llave != -1 and ultima_llave < len(respuesta_raw) - 1:
            respuesta_raw = respuesta_raw[:ultima_llave + 1]

        respuesta_raw = respuesta_raw.strip()

        analisis_json = json_lib.loads(respuesta_raw)

        return jsonify({"analisis": analisis_json})

    except json_lib.JSONDecodeError as e:
        print("ERROR JSON /analizar:", str(e))
        print("Respuesta raw:", respuesta_raw[:500])
        return jsonify({"error": "El modelo no devolvió JSON válido, intenta de nuevo"}), 500

    except Exception as e:
        print("ERROR /analizar:", str(e))
        return jsonify({"error": "Error al generar el análisis"}), 500

# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
