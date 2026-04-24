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

@app.route("/analizar", methods=["POST"])
@jwt_required()
def analizar():
    try:
        data = request.json
 
        if not data:
            return jsonify({"error": "Datos requeridos"}), 400
 
        producto = data.get("producto")
        mercados = data.get("mercados")  # lista de resultados del /cotizar
 
        if not producto or not mercados:
            return jsonify({"error": "Faltan producto o mercados"}), 400
 
        # Construir contexto de mercados para el prompt
        mercados_texto = ""
        for i, m in enumerate(mercados):
            mercados_texto += (
                f"\n{i+1}. {m['pais']} (ciudad: {m['ciudad']}, "
                f"distancia: {m['distancia']} km, "
                f"costo logístico estimado: ${m['costo']} USD, "
                f"peso: {m['peso']} kg)"
            )
 
        prompt = f"""Eres un experto en comercio internacional y exportación con profundo conocimiento de mercados globales. 
Tu cliente es una empresa colombiana ubicada en Bucaramanga, Santander, que desea exportar el siguiente producto: "{producto}".
 
Según el análisis de tendencias globales, los mercados con mayor potencial identificados son:{mercados_texto}
 
Para CADA uno de estos mercados, proporciona un análisis estratégico completo que incluya:
 
1. **Precio de referencia**: Rango de precios típicos del producto en ese mercado (en USD), márgenes esperados y comparación con el costo logístico dado.
2. **Canales de distribución**: Los canales más efectivos para llegar al consumidor final (e-commerce, mayoristas, distribuidores, ferias, etc.).
3. **Requisitos de entrada**: Certificaciones, regulaciones aduaneras, aranceles o barreras técnicas relevantes para exportar este producto desde Colombia a ese mercado.
4. **Estrategia de posicionamiento**: Cómo diferenciarse y posicionarse competitivamente, destacando ventajas del origen colombiano si aplica.
5. **Consideraciones clave**: Aspectos culturales, estacionalidad, competencia local o cualquier factor crítico a tener en cuenta.
 
Sé específico, práctico y directo. Evita generalidades. El análisis debe ser accionable para una PYME exportadora colombiana.
Responde en español. Estructura tu respuesta claramente por mercado con los 5 puntos para cada uno."""
 
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un consultor experto en exportación y comercio internacional. Siempre respondes en español con análisis precisos, prácticos y estructurados."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096,
        )
 
        analisis = completion.choices[0].message.content
 
        return jsonify({"analisis": analisis})
 
    except Exception as e:
        print("ERROR /analizar:", str(e))
        return jsonify({"error": "Error al generar el análisis. Intenta nuevamente."}), 500

# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
