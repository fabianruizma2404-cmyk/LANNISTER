import React, { useState } from "react";
export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const login = async () => {
    const res = await fetch("https://lannister-production.up.railway.app/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.token) {
      localStorage.setItem("token", data.token);
      window.location.href = "/app";
    } else {
      alert("Credenciales incorrectas");
    }
  };

  return (
    <div className="login-box">
      <h2>Login</h2>

      <input onChange={e=>setEmail(e.target.value)} placeholder="Email"/>
      <input type="password" onChange={e=>setPassword(e.target.value)} placeholder="Password"/>

      <button onClick={login}>Entrar</button>
    </div>
  );
}
