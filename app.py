from flask import Flask, request, jsonify
from flask_cors import CORS
from pytrends.request import TrendReq
from googletrans import Translator
import pandas as pd

app = Flask(__name__)
CORS(app)

pytrends = TrendReq(hl='es', tz=360)
translator = Translator()

cache = {}

def top_paises(producto):
    if producto in cache:
        return cache[producto]

    idiomas = ["en", "de", "fr"]
    resultados = pd.DataFrame()

    traducciones = [translator.translate(producto, dest=lang).text for lang in idiomas]

    for palabra in [producto] + traducciones:
        try:
            pytrends.build_payload([palabra], geo='')
            df = pytrends.interest_by_region(resolution='COUNTRY')
            df = df.rename(columns={palabra: palabra})

            if resultados.empty:
                resultados = df
            else:
                resultados = resultados.join(df, how="outer")
        except:
            pass

    resultados["Promedio"] = resultados.mean(axis=1)
    resultados = resultados.sort_values(by="Promedio", ascending=False)

    top3 = resultados.head(3)
    paises = list(top3.index)

    cache[producto] = paises
    return paises

@app.route("/trends")
def trends():
    producto = request.args.get("producto")
    return jsonify({"paises": top_paises(producto)})

app.run(host="0.0.0.0", port=5000)