import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login({ backend }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const nav = useNavigate();

  const login = async () => {
    try {
      const res = await fetch(`${backend}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      if (data.token) {
        localStorage.setItem("token", data.token);

        // ✅ REDIRECCIÓN CORRECTA
        nav("/dashboard");
      } else {
        alert("Credenciales incorrectas");
      }

    } catch (error) {
      alert("Error de conexión con el servidor");
    }
  };

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

      <p onClick={() => nav("/")} className="link">
        ← Volver al inicio
      </p>
    </div>
  );
}
