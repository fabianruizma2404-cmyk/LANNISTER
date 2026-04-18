import React, { useState } from "react";
import Dashboard from "./Dashboard";
import "./styles.css";

const BACKEND_URL = "https://lannister-production.up.railway.app";

export default function App() {
  const [vista, setVista] = useState("home"); // home | login | register | dashboard
  const token = localStorage.getItem("token");

  // 🔁 Si ya está logueado → dashboard
  if (token && vista !== "dashboard") {
    setVista("dashboard");
  }

  return (
    <>
      {vista === "home" && <Home setVista={setVista} />}
      {vista === "login" && <Login setVista={setVista} />}
      {vista === "register" && <Register setVista={setVista} />}
      {vista === "dashboard" && <Dashboard />}
    </>
  );
}

//////////////////////////////////////////////////////////
// 🏠 LANDING PAGE
//////////////////////////////////////////////////////////
function Home({ setVista }) {
  return (
    <div className="home">

      <nav className="navbar">
        <h2>EXPORTIA</h2>
        <div>
          <button onClick={() => setVista("login")}>Login</button>
          <button onClick={() => setVista("register")}>Registro</button>
        </div>
      </nav>

      <section className="hero">
        <h1>Soluciones Logísticas Inteligentes</h1>
        <p>Analiza mercados globales y optimiza tus exportaciones</p>
        <button onClick={() => setVista("login")}>Comenzar</button>
      </section>

      <footer>
        <h3>Exportia</h3>
        <p>Bucaramanga, Santander, Colombia</p>
        <p>exportia@outlook.com</p>
        <p>+57 314 675 8945</p>
      </footer>
    </div>
  );
}

//////////////////////////////////////////////////////////
// 🔐 LOGIN
//////////////////////////////////////////////////////////
function Login({ setVista }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

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
        setVista("dashboard");
      } else {
        alert("Credenciales incorrectas");
      }

    } catch {
      alert("Error de conexión");
    }
  };

  return (
    <div className="auth-box">
      <h2>Login</h2>

      <input
        type="email"
        placeholder="Correo"
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="Contraseña"
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={login}>Ingresar</button>

      <p onClick={() => setVista("home")}>⬅ Volver</p>
    </div>
  );
}

//////////////////////////////////////////////////////////
// 📝 REGISTRO CON CÓDIGO
//////////////////////////////////////////////////////////
function Register({ setVista }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [codigo, setCodigo] = useState("");

  const registrar = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password, codigo })
      });

      const data = await res.json();

      if (data.message) {
        alert("Usuario creado");
        setVista("login");
      } else {
        alert(data.error);
      }

    } catch {
      alert("Error de conexión");
    }
  };

  return (
    <div className="auth-box">
      <h2>Registro</h2>

      <input placeholder="Correo" onChange={e=>setEmail(e.target.value)} />
      <input type="password" placeholder="Contraseña" onChange={e=>setPassword(e.target.value)} />
      <input placeholder="Código de acceso" onChange={e=>setCodigo(e.target.value)} />

      <button onClick={registrar}>Registrarse</button>

      <p onClick={()=>setVista("home")}>⬅ Volver</p>
    </div>
  );
}
