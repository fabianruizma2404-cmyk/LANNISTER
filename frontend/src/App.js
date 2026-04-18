import React, { useState } from "react";
import Dashboard from "./Dashboard";
import "./styles.css";

const BACKEND_URL = "https://lannister-production.up.railway.app";

export default function App() {
  const [view, setView] = useState("home"); // 🔥 CONTROL TOTAL
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

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
        setView("dashboard");
      } else {
        alert("Credenciales incorrectas");
      }

    } catch (error) {
      alert("Error de conexión");
    }
  };

  // 🔓 LOGOUT
  const logout = () => {
    localStorage.removeItem("token");
    setView("home");
  };

  // 🔥 SI YA ESTÁ LOGUEADO
  if (token && view !== "home") {
    return <Dashboard logout={logout} />;
  }

  // 🏠 HOME (LANDING PAGE)
  if (view === "home") {
    return (
      <div className="home">
        <h1>🌍 Exportia</h1>
        <p>Tu aliado en logística inteligente</p>

        <button onClick={() => setView("login")}>
          Iniciar sesión
        </button>

        <button onClick={() => setView("register")}>
          Registrarse
        </button>
      </div>
    );
  }

  // 🔐 LOGIN
  if (view === "login") {
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
          Entrar
        </button>

        <p onClick={() => setView("home")} className="link">
          ← Volver
        </p>
      </div>
    );
  }

  // 📝 REGISTRO (básico por ahora)
  if (view === "register") {
    return (
      <div className="login-box">
        <h2>📝 Registro</h2>

        <input placeholder="Correo" />
        <input placeholder="Contraseña" />
        <input placeholder="Código de acceso" />

        <button>Registrarse</button>

        <p onClick={() => setView("home")} className="link">
          ← Volver
        </p>
      </div>
    );
  }
}
