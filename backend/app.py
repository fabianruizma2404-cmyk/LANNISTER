from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd
import requests
import os
import math
import random

app = Flask(__name__)
CORS(app)

pytrends = TrendReq(hl='es', tz=360)

# 📍 Bucaramanga
ORIGEN = {"lat": 7.119349, "lon": -73.122741}

# 🌍 Traducción
def traducir(texto, idioma):
    try:
        res = requests.post(
            "https://libretranslate.de/translate",
            json={"q": texto, "source": "auto", "target": idioma},
            timeout=5
        )
        return res.json()["translatedText"]
    except:
        return texto

# 🌎 Obtener capital
def obtener_capital(pais):
    try:
        res = requests.get(f"https://restcountries.com/v3.1/name/{pais}")
        data = res.json()
        return data[0]["capital"][0]
    except:
        return pais

# 📍 Geocoding
def geocode(ciudad):
    try:
        key = os.environ.get("d65f4f736b76413792e477ff32b2fc11")
        res = requests.get(
            f"https://api.opencagedata.com/geocode/v1/json?q={ciudad}&key={key}"
        )
        data = res.json()
        return data["results"][0]["geometry"]
    except:
        return {"lat": 0, "lng": 0}

# 📏 Distancia (Haversine)
def distancia(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

# 💰 Cálculo costo
def calcular_envio(ciudad):
    coords = geocode(ciudad)

    peso = random.uniform(2, 6)
    largo = random.uniform(20, 60)
    ancho = random.uniform(20, 60)
    alto = random.uniform(20, 60)

    peso_vol = (largo * ancho * alto) / 5000
    peso_final = max(peso, peso_vol)

    dist = distancia(
        ORIGEN["lat"], ORIGEN["lon"],
        coords["lat"], coords["lng"]
    )

    costo = 25 + peso_final * 6 + dist * 0.015

    if dist > 3000:
        costo *= 1.2

    costo *= 1 + (random.random() * 0.1 - 0.05)

    return {
        "ciudad": ciudad,
        "costo": round(costo, 2),
        "distancia": int(dist),
        "peso": round(peso_final, 2)
    }

# 🧠 Trends + cálculo completo
@app.route("/cotizar")
def cotizar():
    producto = request.args.get("producto")

    if not producto:
        return jsonify({"error": "Producto requerido"}), 400

    idiomas = ["en", "de", "fr"]
    traducciones = [traducir(producto, lang) for lang in idiomas]
    keywords = [producto] + traducciones

    resultados = pd.DataFrame()

    for palabra in keywords:
        try:
            pytrends.build_payload([palabra], geo='')
            df = pytrends.interest_by_region(resolution='COUNTRY')

            if df.empty:
                continue

            df = df.rename(columns={palabra: palabra})

            if resultados.empty:
                resultados = df
            else:
                resultados = resultados.join(df, how="outer")

        except:
            continue

    if resultados.empty:
        return jsonify({"resultados": []})

    resultados["Promedio"] = resultados.mean(axis=1)
    resultados = resultados.sort_values(by="Promedio", ascending=False)

    top3 = resultados.head(3).index.tolist()

    cotizaciones = []

    for pais in top3:
        capital = obtener_capital(pais)
        envio = calcular_envio(capital)

        cotizaciones.append({
            "pais": pais,
            **envio
        })

    return jsonify({"resultados": cotizaciones})

# 🔧 Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
