import React, { useState } from "react";
import "./styles.css";

const API_KEY = "d65f4f736b76413792e477ff32b2fc11";
const BACKEND_URL = "https://lannister-production.up.railway.app";

const ORIGEN = { lat: 7.119349, lon: -73.122741 };

const capitales = {
  "united states": "Washington",
  germany: "Berlin",
  japan: "Tokyo",
  france: "Paris",
  spain: "Madrid",
  italy: "Rome",
  mexico: "Mexico City",
  brazil: "Brasilia",
  argentina: "Buenos Aires",
};

function calcularDistancia(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const toRad = (d) => (d * Math.PI) / 180;

  return R * Math.acos(
    Math.cos(toRad(lat1)) *
    Math.cos(toRad(lat2)) *
    Math.cos(toRad(lon2) - toRad(lon1)) +
    Math.sin(toRad(lat1)) * Math.sin(toRad(lat2))
  );
}

async function geocode(ciudad) {
  const res = await fetch(
    `https://api.opencagedata.com/geocode/v1/json?q=${ciudad}&key=${API_KEY}`
  );
  const data = await res.json();
  return data.results[0].geometry;
}

async function calcularEnvio(ciudad) {
  const destino = await geocode(ciudad);

  const peso = 2 + Math.random() * 5;
  const largo = 20 + Math.random() * 40;
  const ancho = 20 + Math.random() * 40;
  const alto = 20 + Math.random() * 40;

  const pesoVol = (largo * ancho * alto) / 5000;
  const pesoFinal = Math.max(peso, pesoVol);

  const dist = calcularDistancia(
    ORIGEN.lat,
    ORIGEN.lon,
    destino.lat,
    destino.lng
  );

  let costo = 25 + pesoFinal * 6 + dist * 0.015;
  if (dist > 3000) costo *= 1.2;

  return {
    ciudad,
    costo: costo.toFixed(2),
    distancia: dist.toFixed(0),
  };
}

export default function App() {
  const [producto, setProducto] = useState("");
  const [resultados, setResultados] = useState([]);

  const buscar = async () => {
    const res = await fetch(`${BACKEND_URL}/trends?producto=${producto}`);
    const data = await res.json();

    const cotizaciones = [];

    for (let pais of data.paises) {
      const capital = capitales[pais.toLowerCase()] || pais;
      const envio = await calcularEnvio(capital);
      cotizaciones.push(envio);
    }

    setResultados(cotizaciones);
  };

  return (
    <div className="container">
      <h1>🌍 Cotizador Inteligente</h1>

      <input
        placeholder="Producto"
        value={producto}
        onChange={(e) => setProducto(e.target.value)}
      />

      <button onClick={buscar}>Buscar mercados</button>

      {resultados.map((r, i) => (
        <div key={i} className="result">
          <h2>{r.ciudad}</h2>
          <p>${r.costo} USD</p>
          <p>{r.distancia} km</p>
        </div>
      ))}
    </div>
  );
}
