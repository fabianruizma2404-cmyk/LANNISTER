import React, { useState } from "react";
import "./styles.css";

const BACKEND_URL = "https://lannister-production.up.railway.app";

export default function Dashboard({ setVista }) {
  const [producto, setProducto] = useState("");
  const [resultados, setResultados] = useState([]);

  const [peso, setPeso] = useState(3);
  const [largo, setLargo] = useState(30);
  const [ancho, setAncho] = useState(30);
  const [alto, setAlto] = useState(30);

  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  // 🚀 CONSULTAR BACKEND
  const buscar = async () => {
    if (!producto) {
      alert("Ingresa un producto");
      return;
    }

    setLoading(true);
    setResultados([]);

    try {
      const res = await fetch(
        `${BACKEND_URL}/cotizar?producto=${producto}&peso=${peso}&largo=${largo}&ancho=${ancho}&alto=${alto}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      const data = await res.json();

      if (data.error) {
        alert(data.error);
        return;
      }

      setResultados(data.resultados || []);

    } catch (err) {
      alert("Error de conexión con el servidor");
    }

    setLoading(false);
  };

  // 🔓 LOGOUT
  const logout = () => {
    localStorage.removeItem("token");
    window.location.reload(); // vuelve a login
  };
const data = await res.json();
console.log("RESPUESTA BACKEND:", data);
  return (
    <div className="container">

      <button onClick={logout} className="logout">
        Cerrar sesión
      </button>

      <h1>🌍 Explorador de Mercados</h1>

      {/* 🔍 BUSCADOR */}
      <div className="search">
        <input
          placeholder="Ej: zapatos, tecnología..."
          value={producto}
          onChange={(e) => setProducto(e.target.value)}
        />
        <button onClick={buscar}>Analizar</button>
      </div>

      {/* ⚙️ CONTROLES */}
      <div className="controls">
        <input
          type="number"
          value={peso}
          onChange={(e) => setPeso(e.target.value)}
          placeholder="Peso (kg)"
        />
        <input
          type="number"
          value={largo}
          onChange={(e) => setLargo(e.target.value)}
          placeholder="Largo (cm)"
        />
        <input
          type="number"
          value={ancho}
          onChange={(e) => setAncho(e.target.value)}
          placeholder="Ancho (cm)"
        />
        <input
          type="number"
          value={alto}
          onChange={(e) => setAlto(e.target.value)}
          placeholder="Alto (cm)"
        />
      </div>

      {/* ⏳ LOADING */}
      {loading && <p className="loading">Analizando mercados...</p>}

      {/* 📦 RESULTADOS */}
      <div className="cards">
        {resultados.map((r, i) => (
          <div key={i} className="card">
            <h2>{r.pais}</h2>
            <p>📍 {r.ciudad}, {r.pais}</p>
            <p>📏 {r.distancia} km</p>
            <p>⚖️ {r.peso} kg</p>
            <h3>${r.costo} USD</h3>
          </div>
        ))}
      </div>

      {/* 🏢 FOOTER */}
      <footer className="footer">
        <h3>Exportia</h3>
        <p>Bucaramanga, Santander, Colombia</p>
        <p>📧 exportia@outlook.com</p>
        <p>📞 +57 314 675 8945</p>
      </footer>

    </div>
  );
}
