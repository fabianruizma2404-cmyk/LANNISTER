from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd
import requests
import os
import math
import time
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route("/cotizar")
@jwt_required()
def cotizar():
    usuario = get_jwt_identity()
    print("Usuario autenticado:", usuario)
app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

db = SQLAlchemy(app)
jwt = JWTManager(app)



# 🔥 Pytrends más estable
pytrends = TrendReq(
    hl='es',
    tz=360,
    timeout=(10, 25),
    retries=2,
    backoff_factor=0.1
)

# 📍 Bucaramanga
ORIGEN = {"lat": 7.119349, "lon": -73.122741}
OPENCAGE_KEY = "d65f4f736b76413792e477ff32b2fc11"

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# 🌍 Traducción (NO rompe flujo)
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

# 🌎 Capital
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

# 💰 Cálculo
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

# 🧠 TRENDS MULTILENGUAJE (CORREGIDO)
def top_paises_multilingue(producto):
    idiomas = ["en", "de", "fr"]
    resultados = pd.DataFrame()

    print("Traduciendo...")

    traducciones = [traducir(producto, lang) for lang in idiomas]
    keywords = list(set([producto] + traducciones))

    print("Keywords:", keywords)

    for palabra in keywords:
        try:
            print("Consultando:", palabra)

            pytrends.build_payload(
                [palabra],
                timeframe='today 12-m',
                geo=''
            )

            df = pytrends.interest_by_region(
                resolution='COUNTRY',
                inc_low_vol=True
            )

            time.sleep(1)  # 🔥 evita bloqueo

            if df.empty:
                print("Sin datos para:", palabra)
                continue

            df = df.rename(columns={palabra: palabra})

            if resultados.empty:
                resultados = df
            else:
                resultados = resultados.join(df, how="outer")

        except Exception as e:
            print("Error en palabra:", palabra, str(e))
            continue

    if resultados.empty:
        raise Exception("Google Trends bloqueado o sin datos")

    resultados["Promedio"] = resultados.mean(axis=1)
    resultados = resultados.sort_values(by="Promedio", ascending=False)

    top3 = resultados.head(3).index.tolist()

    print("Top países:", top3)

    if len(top3) < 3:
        raise Exception("Menos de 3 países")

    return top3

# 🚀 ENDPOINT
@app.route("/init-db")
def init_db():
    db.create_all()
    return "DB lista"

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    hashed = generate_password_hash(data["password"])

    user = Usuario(
        email=data["email"],
        password=hashed
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = Usuario.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(identity=user.id)

    return jsonify({"token": token})


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

        print("=== NUEVA CONSULTA ===")
        print("Producto:", producto)

        paises = top_paises_multilingue(producto)

        resultados = []

        for pais in paises:
            print("Procesando:", pais)

            capital = obtener_capital(pais)
            print("Capital:", capital)

            envio = calcular_envio(capital, pais, peso, largo, ancho, alto)
            resultados.append(envio)

        return jsonify({"resultados": resultados})

    except Exception as e:
        print("ERROR FINAL:", str(e))

        return jsonify({
            "error": "Estamos presentando fallos con servicios externos. Intenta nuevamente más tarde."
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
