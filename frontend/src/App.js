import React, { useState, useEffect } from "react";
import Dashboard from "./pages/Dashboard";
import "./styles.css";

const BACKEND_URL = "https://lannister-production.up.railway.app";

export default function App() {
  const [view, setView] = useState("home");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const token = localStorage.getItem("token");

  // 🔥 CONTROL DE SESIÓN AL CARGAR
  useEffect(() => {
    if (token) {
      setView("dashboard");
    } else {
      setView("home");
    }
  }, []);

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

  // 📝 REGISTER REAL
  const register = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (res.ok) {
        alert("Usuario creado correctamente");
        setView("login");
      } else {
        alert(data.error || "Error en registro");
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

  // 🔥 SI ESTÁ LOGUEADO → DASHBOARD
  if (view === "dashboard" && token) {
    return <Dashboard logout={logout} />;
  }

  // 🏠 HOME
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

  // 📝 REGISTER
  if (view === "register") {
    return (
      <div className="login-box">
        <h2>📝 Registro</h2>

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

        <button onClick={register}>
          Registrarse
        </button>

        <p onClick={() => setView("home")} className="link">
          ← Volver
        </p>
      </div>
    );
  }
}
