import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const CODIGO_SECRETO = "EXPORTIA2026";

export default function Register({ backend }) {
  const [form, setForm] = useState({
    nombre: "",
    empresa: "",
    email: "",
    password: "",
    confirmPassword: "",
    sector: "",
    codigo: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [aceptaTerminos, setAceptaTerminos] = useState(false);
  const nav = useNavigate();

  const set = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const validate = () => {
    if (!form.nombre.trim()) return "El nombre es obligatorio.";
    if (!form.email.trim()) return "El correo es obligatorio.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      return "Ingresa un correo válido.";
    if (form.password.length < 8)
      return "La contraseña debe tener al menos 8 caracteres.";
    if (form.password !== form.confirmPassword)
      return "Las contraseñas no coinciden.";
   if (form.codigo.trim() !== CODIGO_SECRETO)
      return "Código de acceso inválido. Contáctanos para obtenerlo.";
    if (!aceptaTerminos)
      return "Debes aceptar los términos y condiciones.";
    return null;
  };

  const registrar = async () => {
    const err = validate();
    if (err) { setError(err); return; }
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${backend}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          nombre: form.nombre,
          empresa: form.empresa,
          sector: form.sector,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess(true);
        setTimeout(() => nav("/login"), 2800);
      } else {
        setError(data.error || "Error en el registro. Intenta de nuevo.");
      }
    } catch {
      setError("Error de conexión con el servidor.");
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => { if (e.key === "Enter") registrar(); };

  /* ---- PANTALLA DE ÉXITO ---- */
  if (success) {
    return (
      <div className="auth-root">
        <div className="auth-bg-grid" aria-hidden="true" />
        <div className="auth-success-screen">
          <div className="auth-success-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h2 className="auth-success-title">¡Cuenta creada!</h2>
          <p className="auth-success-sub">
            Bienvenido a Exportia, <strong>{form.nombre}</strong>.<br />
            Redirigiendo al inicio de sesión…
          </p>
          <div className="auth-success-bar">
            <div className="auth-success-bar-fill" />
          </div>
        </div>
      </div>
    );
  }

  /* ---- FORMULARIO ---- */
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
            Tu puerta de entrada<br />a mercados <em>globales</em>
          </h2>
          <p className="auth-left-sub">
            Únete a la plataforma que combina inteligencia artificial con
            experiencia en comercio exterior para llevar tus productos al mundo.
          </p>

          {/* Beneficios */}
          <div className="auth-benefits">
            {[
              { label: "Análisis de 180+ mercados internacionales" },
              { label: "Agentes IA para documentos de exportación" },
              { label: "Consultoría y estrategia personalizada" },
              { label: "Cumplimiento normativo automatizado" },
            ].map((b) => (
              <div className="auth-benefit-item" key={b.label}>
                <div className="auth-benefit-check">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <span>{b.label}</span>
              </div>
            ))}
          </div>

          <div className="auth-left-stats" style={{ marginTop: "2.5rem" }}>
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
      <div className="auth-right auth-right--register">
        <div className="auth-form-card auth-form-card--wide">
          <div className="auth-form-header">
            <p className="auth-form-eyebrow">Acceso exclusivo</p>
            <h1 className="auth-form-title">Crear cuenta</h1>
          </div>

          <div className="auth-fields">
            {/* Fila 1: nombre + empresa */}
            <div className="auth-fields-grid">
              <div className="auth-field-group">
                <label className="auth-label">Nombre completo *</label>
                <input
                  className="auth-input"
                  type="text"
                  placeholder="Tu nombre"
                  value={form.nombre}
                  onChange={set("nombre")}
                  onKeyDown={handleKey}
                  autoComplete="name"
                />
              </div>
              <div className="auth-field-group">
                <label className="auth-label">Empresa <span className="auth-optional">opcional</span></label>
                <input
                  className="auth-input"
                  type="text"
                  placeholder="Nombre de tu empresa"
                  value={form.empresa}
                  onChange={set("empresa")}
                  onKeyDown={handleKey}
                  autoComplete="organization"
                />
              </div>
            </div>

            {/* Correo */}
            <div className="auth-field-group">
              <label className="auth-label">Correo electrónico *</label>
              <input
                className="auth-input"
                type="email"
                placeholder="tu@correo.com"
                value={form.email}
                onChange={set("email")}
                onKeyDown={handleKey}
                autoComplete="email"
              />
            </div>

            {/* Sector */}
            <div className="auth-field-group">
              <label className="auth-label">Sector exportador <span className="auth-optional">opcional</span></label>
              <select
                className="auth-select"
                value={form.sector}
                onChange={set("sector")}
              >
                <option value="">Selecciona tu sector</option>
                <option value="agroindustria">Agroindustria</option>
                <option value="textil">Textil y confección</option>
                <option value="manufactura">Manufactura</option>
                <option value="tecnologia">Tecnología y software</option>
                <option value="alimentos">Alimentos y bebidas</option>
                <option value="mineria">Minería y energía</option>
                <option value="servicios">Servicios</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            {/* Fila 2: contraseñas */}
            <div className="auth-fields-grid">
              <div className="auth-field-group">
                <label className="auth-label">Contraseña *</label>
                <div className="auth-input-wrapper">
                  <input
                    className="auth-input auth-input--icon"
                    type={showPassword ? "text" : "password"}
                    placeholder="Mín. 8 caracteres"
                    value={form.password}
                    onChange={set("password")}
                    onKeyDown={handleKey}
                    autoComplete="new-password"
                  />
                  <button
                    className="auth-eye"
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" />
                        <line x1="1" y1="1" x2="23" y2="23" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
              <div className="auth-field-group">
                <label className="auth-label">Confirmar contraseña *</label>
                <input
                  className="auth-input"
                  type={showPassword ? "text" : "password"}
                  placeholder="Repite tu contraseña"
                  value={form.confirmPassword}
                  onChange={set("confirmPassword")}
                  onKeyDown={handleKey}
                  autoComplete="new-password"
                />
              </div>
            </div>

            {/* Código secreto */}
            <div className="auth-field-group">
              <label className="auth-label">
                Código de acceso *
                <span className="auth-label-hint"> — Solicitado al equipo Exportia</span>
              </label>
              <input
                className="auth-input auth-input--code"
                type="text"
                placeholder="XXXXXXXX0000"
                value={form.codigo}
                onChange={(e) => setForm((prev) => ({ ...prev, codigo: e.target.value.trim() }))}
                onKeyDown={handleKey}
                autoComplete="off"
                spellCheck={false}
              />
            </div>

            {/* Términos */}
            <div className="auth-checkbox-group">
              <input
                className="auth-checkbox"
                type="checkbox"
                id="terminos"
                checked={aceptaTerminos}
                onChange={(e) => setAceptaTerminos(e.target.checked)}
              />
              <label className="auth-checkbox-label" htmlFor="terminos">
                Acepto los <a href="#">términos y condiciones</a> y la{" "}
                <a href="#">política de privacidad</a> de Exportia.
              </label>
            </div>

            {error && <p className="auth-error">{error}</p>}

            <button
              className="auth-btn-primary"
              onClick={registrar}
              disabled={loading}
            >
              {loading ? <span className="auth-spinner" /> : "Crear mi cuenta"}
            </button>
          </div>

          <div className="auth-divider">
            <span />
            <p>¿Ya tienes cuenta?</p>
            <span />
          </div>

          <button className="auth-btn-ghost" onClick={() => nav("/login")}>
            Iniciar sesión
          </button>

          <p className="auth-back" onClick={() => nav("/")}>
            ← Volver al inicio
          </p>
        </div>
      </div>
    </div>
  );
}
