from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd
import requests
import os
import math

app = Flask(__name__)
CORS(app)

pytrends = TrendReq(hl='es', tz=360)

# 📍 Bucaramanga
ORIGEN = {"lat": 7.119349, "lon": -73.122741}

# 🌍 Traducción ROBUSTA (NO rompe flujo)
def traducir(texto, idioma):
    try:
        res = requests.post(
            "https://libretranslate.de/translate",
            json={
                "q": texto,
                "source": "auto",
                "target": idioma
            },
            timeout=5
        )

        if res.status_code == 200:
            return res.json()["translatedText"]

        return texto  # fallback

    except:
        return texto  # 🔥 clave: no romper

# 🌎 Obtener capital
def obtener_capital(pais):
    try:
        res = requests.get(f"https://restcountries.com/v3.1/name/{pais}", timeout=5)

        if res.status_code != 200:
            raise Exception()

        data = res.json()

        if isinstance(data, list) and "capital" in data[0]:
            return data[0]["capital"][0]

        return pais

    except:
        raise Exception(f"No se pudo obtener capital de {pais}")

# 📍 Geocoding
def geocode(ciudad):
    try:
        key = os.environ.get("OPENCAGE_KEY")

        res = requests.get(
            f"https://api.opencagedata.com/geocode/v1/json?q={ciudad}&key={key}",
            timeout=5
        )

        if res.status_code != 200:
            raise Exception()

        data = res.json()

        if not data["results"]:
            raise Exception()

        return data["results"][0]["geometry"]

    except:
        raise Exception(f"No se pudo geocodificar {ciudad}")

# 📏 Distancia (Haversine)
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

# 🧠 FUNCIÓN ORIGINAL DE TRENDS (MULTILENGUAJE)
def top_paises_multilingue(producto):
    idiomas = ["en", "de", "fr"]
    resultados = pd.DataFrame()

    # 🔥 Traducciones (pero tolerante a fallos)
    traducciones = [traducir(producto, lang) for lang in idiomas]
    keywords = [producto] + traducciones

    for palabra in keywords:
        try:
            pytrends.build_payload(
                [palabra],
                timeframe='today 12-m',
                geo=''
            )

            df = pytrends.interest_by_region(
                resolution='COUNTRY',
                inc_low_vol=True
            )

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
        raise Exception("No se pudieron obtener datos de Google Trends")

    resultados["Promedio"] = resultados.mean(axis=1)
    resultados = resultados.sort_values(by="Promedio", ascending=False)

    return resultados.head(3).index.tolist()

# 🚀 ENDPOINT PRINCIPAL
@app.route("/cotizar")
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

        if len(paises) < 3:
            raise Exception("No suficientes países")

        resultados = []

        for pais in paises:
            capital = obtener_capital(pais)
            envio = calcular_envio(capital, pais, peso, largo, ancho, alto)
            resultados.append(envio)

        return jsonify({"resultados": resultados})

    except Exception as e:
        print("ERROR:", str(e))  # 🔥 útil para logs en Railway

        return jsonify({
            "error": "Estamos presentando fallos con servicios externos. Intenta nuevamente más tarde."
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
