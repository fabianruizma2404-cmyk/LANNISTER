import React, { useState } from "react";
import "./styles.css";

const BACKEND_URL = "https://lannister-production.up.railway.app";

export default function App() {
  const [producto, setProducto] = useState("");
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(false);

  const buscar = async () => {
    if (!producto) return;

    setLoading(true);
    setResultados([]);

    try {
      const res = await fetch(
        `${BACKEND_URL}/cotizar?producto=${producto}`
      );
      const data = await res.json();

      setResultados(data.resultados);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>🌍 Explorador de Mercados</h1>

      <div className="search">
        <input
          placeholder="Ej: zapatos, ropa, tecnología..."
          value={producto}
          onChange={(e) => setProducto(e.target.value)}
        />
        <button onClick={buscar}>Analizar</button>
      </div>

      {loading && <p className="loading">Analizando mercados...</p>}

      <div className="cards">
        {resultados.map((r, i) => (
          <div key={i} className="card">
            <h2>{r.pais}</h2>
            <p>📍 {r.ciudad}</p>
            <p>📏 {r.distancia} km</p>
            <p>⚖️ {r.peso} kg</p>
            <h3>${r.costo} USD</h3>
          </div>
        ))}
      </div>
    </div>
  );
}
