import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const CODIGO_SECRETO = "EXPORTIA2026";

export default function Register({ backend }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [codigo, setCodigo] = useState("");
  const nav = useNavigate();

  const registrar = async () => {

    // 🔐 VALIDACIÓN DEL CÓDIGO
    if (codigo !== CODIGO_SECRETO) {
      alert("Código inválido");
      return;
    }

    try {
      const res = await fetch(`${backend}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();

      // ✅ VALIDACIÓN CORRECTA
      if (res.ok) {
        alert("Usuario creado correctamente");

        // 🔁 REDIRECCIÓN A LOGIN
        nav("/login");
      } else {
        alert(data.error || "Error en el registro");
      }

    } catch (error) {
      alert("Error de conexión con el servidor");
    }
  };

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

      <input
        placeholder="Código de acceso"
        value={codigo}
        onChange={(e) => setCodigo(e.target.value)}
      />

      <button onClick={registrar}>
        Registrarse
      </button>

      <p onClick={() => nav("/")} className="link">
        ← Volver al inicio
      </p>
    </div>
  );
}
