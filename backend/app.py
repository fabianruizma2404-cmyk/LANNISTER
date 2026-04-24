from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd
import requests
import os
import math
import time
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from groq import Groq

app = Flask(__name__)
CORS(app)

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 🔥 FIX SUPABASE (MUY IMPORTANTE)
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

# 🔥 Pytrends estable
pytrends = TrendReq(
    hl='es',
    tz=360,
    timeout=(10, 25),
    retries=2,
    backoff_factor=0.1
)

# 📍 Origen (Bucaramanga)
ORIGEN = {"lat": 7.119349, "lon": -73.122741}

# 👤 Modelo Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(150), nullable=True)
    empresa = db.Column(db.String(150), nullable=True)
    sector = db.Column(db.String(100), nullable=True)

# 🌍 Traducción
def traducir(texto, idioma):
    try:
        res = requests.post(
            "https://libretranslate.de/translate",
            json={"q": texto, "source": "auto", "target": idioma},
            timeout=5
        )
        if res.status_code == 200:
            return res.json()["translatedText"]
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

# 📍 Geocoding
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
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

# 💰 Cálculo de envío
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

# 🧠 Google Trends multilenguaje
def top_paises_multilingue(producto):
    idiomas = ["en", "de", "fr"]
    resultados = pd.DataFrame()

    traducciones = [traducir(producto, lang) for lang in idiomas]
    keywords = list(set([producto] + traducciones))

    for palabra in keywords:
        try:
            pytrends.build_payload([palabra], timeframe='today 12-m', geo='')

            df = pytrends.interest_by_region(
                resolution='COUNTRY',
                inc_low_vol=True
            )

            time.sleep(1)

            if df.empty:
                continue

            if resultados.empty:
                resultados = df
            else:
                resultados = resultados.join(df, how="outer")

        except:
            continue

    if resultados.empty:
        raise Exception("Google Trends sin datos")

    resultados["Promedio"] = resultados.mean(axis=1)
    resultados = resultados.sort_values(by="Promedio", ascending=False)

    top3 = resultados.head(3).index.tolist()

    if len(top3) < 3:
        raise Exception("Menos de 3 países")

    return top3

# 🚀 INIT DB (opcional)
@app.route("/init-db")
def init_db():
    db.create_all()
    return "DB lista"

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
    usuario = get_jwt_identity()
    print("Usuario autenticado:", usuario)

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
        print("ERROR FINAL:", str(e))

        return jsonify({
            "error": "Estamos presentando fallos con servicios externos. Intenta nuevamente más tarde."
        }), 500

# ============================================================
# EXPORTIA — Endpoint /analizar v2 con Groq + LLaMA 3.3
# Respuesta estructurada en JSON para parseo confiable
# ============================================================
# Reemplaza el endpoint /analizar anterior en app.py
# Los imports y groq_client ya deben estar del paso anterior
# ============================================================

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

        mercados_texto = ""
        for i, m in enumerate(mercados):
            mercados_texto += (
                f"\nMercado {i+1}: {m['pais']} "
                f"(ciudad principal: {m['ciudad']}, "
                f"distancia desde Bucaramanga: {m['distancia']} km, "
                f"costo logístico estimado: ${m['costo']} USD, "
                f"peso del envío: {m['peso']} kg)"
            )

       prompt = f"""Eres un consultor senior de comercio exterior con 20 años de experiencia asesorando PYMEs colombianas en exportación. Conoces en detalle los acuerdos comerciales de Colombia, aranceles, incoterms, operadores logísticos y estrategias reales de entrada a mercados internacionales.

Tu cliente exporta desde Bucaramanga, Colombia: "{producto}"
Peso del envío: {mercados[0]['peso']} kg | Origen: Bucaramanga, Santander, Colombia

MERCADOS IDENTIFICADOS POR ANÁLISIS DE TENDENCIAS:{mercados_texto}

INSTRUCCIÓN CRÍTICA: Responde ÚNICAMENTE con JSON válido puro, sin texto adicional, sin markdown, sin bloques de código.

Para cada mercado debes investigar y proporcionar información ESPECÍFICA y REAL de ese país, no genérica. Si el análisis de dos mercados parece similar, estás haciendo algo mal. Cada mercado tiene su propio contexto arancelario, cultural y logístico.

JSON requerido:
{{
  "mercados": [
    {{
      "pais": "nombre exacto del país",
      "ciudad": "ciudad capital o principal",
      "analisis": {{
        "Precios REALES y específicos del producto '{producto}' en {mercados[0].get('pais', 'este mercado') if mercados else 'este mercado'} (en USD por unidad o kg según aplique). Incluye: precio al consumidor final, precio mayorista, margen bruto estimado para el exportador colombiano, y análisis de si el costo logístico de ${mercados[0]['costo'] if mercados else 0} USD es viable según el volumen mínimo de exportación necesario para ser rentable.",

        "aranceles_y_tratados": "Arancel de importación ESPECÍFICO que aplica para '{producto}' en este país (porcentaje exacto o rango). Indica si Colombia tiene TLC o acuerdo preferencial con este país que reduzca el arancel — menciona el nombre del tratado si existe. Explica el régimen aduanero, si aplica IVA a importaciones, y cualquier arancel antidumping o salvaguardia relevante para este producto.",

        "incoterms_recomendados": "Incoterm(s) recomendados para exportar '{producto}' desde Bucaramanga hacia {mercados[0]['ciudad'] if mercados else 'este destino'}, explicando POR QUÉ ese incoterm es el más conveniente para una PYME colombiana sin experiencia logística internacional. Describe cómo se distribuyen los costos y riesgos, qué documentos se requieren, y qué tipo de seguro de carga se recomienda para esta ruta específica.",

        "canales_y_compradores": "Canales de distribución ESPECÍFICOS para '{producto}' en este mercado: nombres de marketplaces locales relevantes, tipos de importadores o distribuidores que buscar, ferias internacionales del sector donde se puede hacer contacto (con nombres reales), y estrategia concreta de prospección de compradores — cómo contactarlos, qué plataformas B2B usar (Alibaba, Europages, etc.) y qué propuesta de valor resaltar siendo de origen colombiano.",

        "requisitos_y_certificaciones": "Requisitos técnicos, sanitarios y legales ESPECÍFICOS para importar '{producto}' en este país: certificaciones obligatorias (con nombre de la entidad que las emite), etiquetado requerido (idioma, información mínima), normas técnicas aplicables, registro sanitario si aplica, y documentos aduaneros indispensables (factura comercial, certificado de origen, packing list, BL o AWB). Indica si el certificado de origen colombiano da algún beneficio arancelario.",

        "estrategia_entrada": "Plan de acercamiento concreto para entrar a este mercado específico en los próximos 6 meses: paso a paso desde la búsqueda del primer comprador hasta el primer envío. Incluye: plataformas de inteligencia comercial a usar (Legiscomex, Trademap, etc.), ferias o misiones comerciales relevantes, estrategia de precio de introducción, forma de pago recomendada (carta de crédito, pago anticipado, etc.), y consideraciones culturales o de negociación específicas de este país que una PYME colombiana debe conocer."
      }}
    }}
  ]
}}

IMPORTANTE: Genera análisis para los {len(mercados)} mercados. Cada análisis debe ser COMPLETAMENTE DIFERENTE porque cada país tiene su propio contexto. Usa datos reales: aranceles reales, nombres de tratados reales, plataformas reales, ferias reales. Si no conoces el arancel exacto, da un rango realista basado en el sector del producto."""

completion = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": """Eres un consultor experto en comercio exterior colombiano. Tienes conocimiento profundo de:
- Los TLC de Colombia (con USA, UE, CAN, Mercosur, Corea, etc.)
- Aranceles del Sistema Armonizado por partidas arancelarias
- Incoterms 2020 y su aplicación práctica para PYMEs
- Plataformas de inteligencia comercial (Legiscomex, Trademap, Siex)
- Ferias internacionales por sector
- Estrategias de prospección B2B internacional
Siempre respondes con JSON puro válido, sin texto adicional ni markdown. Cada mercado recibe análisis único y específico basado en la realidad de ese país."""
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.6,
    max_tokens=6000,
)

        respuesta_raw = completion.choices[0].message.content.strip()

        # Limpiar posibles bloques markdown que el modelo agregue
        if respuesta_raw.startswith("```"):
            respuesta_raw = respuesta_raw.split("```")[1]
            if respuesta_raw.startswith("json"):
                respuesta_raw = respuesta_raw[4:]
        if respuesta_raw.endswith("```"):
            respuesta_raw = respuesta_raw[:-3]

        respuesta_raw = respuesta_raw.strip()

        import json as json_lib
        analisis_json = json_lib.loads(respuesta_raw)

        return jsonify({"analisis": analisis_json})

    except Exception as e:
        print("ERROR /analizar:", str(e))
        return jsonify({"error": "Error al generar el análisis. Intenta nuevamente."}), 500

# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
