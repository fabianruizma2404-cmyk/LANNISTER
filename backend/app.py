from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

pytrends = TrendReq(hl='es', tz=360)

# 🧠 Obtener top países sin traducción
def top_paises(producto):
    try:
        # Variaciones simples (mejor que solo 1 palabra)
        keywords = [
            producto,
            producto + " online",
            producto + " shop"
        ]

        pytrends.build_payload(keywords, geo='')
        df = pytrends.interest_by_region(resolution='COUNTRY')

        if df.empty:
            return []

        # Promedio entre keywords
        df["Promedio"] = df.mean(axis=1)
        df = df.sort_values(by="Promedio", ascending=False)

        top3 = df.head(3)

        return list(top3.index)

    except Exception as e:
        print("ERROR:", e)
        return []

# 🌍 Endpoint
@app.route("/trends")
def trends():
    producto = request.args.get("producto")

    if not producto:
        return jsonify({"error": "Producto requerido"}), 400

    paises = top_paises(producto)

    return jsonify({"paises": paises})

# 🔧 Compatible con Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
