import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./styles.css";

export default function Login({ backend }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const nav = useNavigate();

  const login = async () => {
    if (!email || !password) {
      setError("Por favor completa todos los campos.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${backend}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (data.token) {
        localStorage.setItem("token", data.token);
        nav("/dashboard");
      } else {
        setError("Credenciales incorrectas. Intenta de nuevo.");
      }
    } catch {
      setError("Error de conexión con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") login();
  };

  return (
    <div className="auth-root">
      <div className="auth-bg-grid" aria-hidden="true" />

      {/* Panel izquierdo — branding */}
      <div className="auth-left">
        <div className="auth-left-inner">
          <div className="exp-logo" style={{ marginBottom: "3rem" }}>
            <span className="exp-logo-dot" />
            EXPORTIA
          </div>
          <h2 className="auth-left-title">
            Inteligencia global<br />para tu <em>negocio</em>
          </h2>
          <p className="auth-left-sub">
            Accede a análisis de mercados, agentes IA y herramientas de
            exportación diseñadas para llevar tus productos al mundo.
          </p>
          <div className="auth-left-stats">
            <div className="auth-left-stat">
              <span className="auth-left-stat-num">180+</span>
              <span className="auth-left-stat-label">Mercados</span>
            </div>
            <div className="auth-left-stat">
              <span className="auth-left-stat-num">4</span>
              <span className="auth-left-stat-label">Agentes IA</span>
            </div>
            <div className="auth-left-stat">
              <span className="auth-left-stat-num">98%</span>
              <span className="auth-left-stat-label">Precisión</span>
            </div>
          </div>
        </div>
      </div>

      {/* Panel derecho — formulario */}
      <div className="auth-right">
        <div className="auth-form-card">
          <div className="auth-form-header">
            <p className="auth-form-eyebrow">Bienvenido de nuevo</p>
            <h1 className="auth-form-title">Iniciar sesión</h1>
          </div>

          <div className="auth-fields">
            <div className="auth-field-group">
              <label className="auth-label">Correo electrónico</label>
              <input
                className="auth-input"
                type="email"
                placeholder="tu@correo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={handleKey}
                autoComplete="email"
              />
            </div>

            <div className="auth-field-group">
              <div className="auth-label-row">
                <label className="auth-label">Contraseña</label>
                <span className="auth-forgot">¿Olvidaste tu contraseña?</span>
              </div>
              <input
                className="auth-input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={handleKey}
                autoComplete="current-password"
              />
            </div>

            {error && <p className="auth-error">{error}</p>}

            <button
              className="auth-btn-primary"
              onClick={login}
              disabled={loading}
            >
              {loading ? (
                <span className="auth-spinner" />
              ) : (
                "Entrar a Exportia"
              )}
            </button>
          </div>

          <div className="auth-divider">
            <span />
            <p>¿No tienes cuenta?</p>
            <span />
          </div>

          <button
            className="auth-btn-ghost"
            onClick={() => nav("/registro")}
          >
            Crear cuenta gratis
          </button>

          <p className="auth-back" onClick={() => nav("/")}>
            ← Volver al inicio
          </p>
        </div>
      </div>
    </div>
  );
}
