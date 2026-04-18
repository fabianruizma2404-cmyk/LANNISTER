import React, { useState } from "react";
const CODIGO_SECRETO = "EXPORTIA2026";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [codigo, setCodigo] = useState("");

  const registrar = async () => {

    if (codigo !== CODIGO_SECRETO) {
      alert("Código inválido");
      return;
    }

    const res = await fetch("https://lannister-production.up.railway.app/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.msg) {
      alert("Usuario creado");
    } else {
      alert("Error");
    }
  };

  return (
    <div className="login-box">
      <h2>Registro</h2>

      <input placeholder="Email" onChange={e=>setEmail(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e=>setPassword(e.target.value)} />
      <input placeholder="Código de acceso" onChange={e=>setCodigo(e.target.value)} />

      <button onClick={registrar}>Registrarse</button>
    </div>
  );
}
