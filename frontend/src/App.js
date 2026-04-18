import React, { useState } from "react";
import "./styles.css";

const BACKEND_URL = "https://lannister-production.up.railway.app";

export default function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [producto, setProducto] = useState("");
  const [resultados, setResultados] = useState([]);

  const [peso, setPeso] = useState(3);
  const [largo, setLargo] = useState(30);
  const [ancho, setAncho] = useState(30);
  const [alto, setAlto] = useState(30);

  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  // 🔐 LOGIN
  const login = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (data.token) {
        localStorage.setItem("token", data.token);
        window.location.reload(); // 🔥 recarga app
      } else {
        alert("Credenciales incorrectas");
      }

    } catch (error) {
      alert("Error de conexión");
    }
  };

  // 🚀 BUSCAR
  const buscar = async () => {
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
    window.location.reload();
  };

  // 🔴 SI NO HAY TOKEN → LOGIN
  if (!token) {
    return (
      <div className="login-box">
        <h2>🔐 Login</h2>

        <input
          type="email"
          placeholder="Correo"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={login}>
          Iniciar sesión
        </button>
      </div>
    );
  }

  // 🟢 SI HAY TOKEN → APP
  return (
    <div className="container">
      <button onClick={logout} className="logout">Cerrar sesión</button>

      <h1>🌍 Explorador de Mercados</h1>

      <div className="search">
        <input
          placeholder="Ej: zapatos, tecnología..."
          value={producto}
          onChange={(e) => setProducto(e.target.value)}
        />
        <button onClick={buscar}>Analizar</button>
      </div>

      <div className="controls">
        <input type="number" value={peso} onChange={(e)=>setPeso(e.target.value)} />
        <input type="number" value={largo} onChange={(e)=>setLargo(e.target.value)} />
        <input type="number" value={ancho} onChange={(e)=>setAncho(e.target.value)} />
        <input type="number" value={alto} onChange={(e)=>setAlto(e.target.value)} />
      </div>

      {loading && <p className="loading">Analizando...</p>}

      <div className="cards">
        {Array.isArray(resultados) && resultados.map((r, i) => (
          <div key={i} className="card">
            <h2>{r.pais}</h2>
            <p>📍 {r.ciudad}, {r.pais}</p>
            <p>📏 {r.distancia} km</p>
            <p>⚖️ {r.peso} kg</p>
            <h3>${r.costo} USD</h3>
          </div>
        ))}
      </div>

      <footer className="footer">
        <h3>Exportia</h3>
        <p>Bucaramanga, Santander, Colombia</p>
        <p>📧 exportia@outlook.com</p>
        <p>📞 +57 314 675 8945</p>
      </footer>
    </div>
  );
}
