import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles.css";

export default function Dashboard() {
  const BACKEND_URL = "https://lannister-production.up.railway.app";
  const nav = useNavigate();
  const [producto, setProducto] = useState("");
  const [resultados, setResultados] = useState([]);
  const [peso, setPeso] = useState(3);
  const [largo, setLargo] = useState(30);
  const [ancho, setAncho] = useState(30);
  const [alto, setAlto] = useState(30);
  const [loading, setLoading] = useState(false);
  const [buscado, setBuscado] = useState("");
  const token = localStorage.getItem("token");

  const logout = () => {
    localStorage.removeItem("token");
    nav("/");
  };

  const buscar = async () => {
    if (!producto.trim()) return;
    if (!token) { nav("/login"); return; }
    setLoading(true);
    setResultados([]);
    setBuscado(producto);
    try {
      const res = await fetch(
        `${BACKEND_URL}/cotizar?producto=${producto}&peso=${peso}&largo=${largo}&ancho=${ancho}&alto=${alto}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await res.json();
      if (!res.ok || data.error) { setLoading(false); return; }
      setResultados(data.resultados || []);
    } catch {
      // conexión fallida
    }
    setLoading(false);
  };

  const ejecutarTradeAdvisor = () => {
    nav("/tradeadvisor", {
      state: { producto: buscado, mercados: resultados },
    });
  };

  const handleKey = (e) => { if (e.key === "Enter") buscar(); };
  const rankLabel = (i) => ["Mayor potencial", "Alto potencial", "Potencial medio"][i] || "Potencial";
  const rankColor = (i) => ["#1DFFA3", "#5B9CF6", "#A78BFA"][i] || "#E8EFF8";

  return (
    <div className="dash-root">
      <div className="auth-bg-grid" aria-hidden="true" />

      {/* ── NAV ── */}
      <nav className="dash-nav">
        <div className="exp-logo">
          <span className="exp-logo-dot" />
          EXPORTIA
        </div>
        <div className="dash-nav-center">
          <span className="dash-nav-tag">
            <span className="dash-nav-dot" />
            Agente MarketScan
          </span>
        </div>
        <button className="dash-logout" onClick={logout}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
          Cerrar sesión
        </button>
      </nav>

      {/* ── HERO ── */}
      <div className="dash-hero">
        <p className="dash-hero-eyebrow">— Inteligencia de mercados globales</p>
        <h1 className="dash-hero-title">
          ¿Qué producto quieres<br />
          <em>exportar al mundo?</em>
        </h1>
        <p className="dash-hero-sub">
          El agente analiza tendencias globales en tiempo real y calcula
          los mejores mercados destino para tu producto.
        </p>
        <div className="dash-search-box">
          <svg className="dash-search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            className="dash-search-input"
            placeholder="Ej: café colombiano, calzado, textiles..."
            value={producto}
            onChange={(e) => setProducto(e.target.value)}
            onKeyDown={handleKey}
          />
          <button className="dash-search-btn" onClick={buscar} disabled={loading || !producto.trim()}>
            {loading
              ? <span className="auth-spinner" style={{ width: 16, height: 16, borderTopColor: "#050F1C" }} />
              : "Analizar"}
          </button>
        </div>
      </div>

      {/* ── DIMENSIONES ── */}
      <div className="dash-dims-section">
        <div className="dash-dims-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
          </svg>
          <span>Especificaciones del paquete</span>
        </div>
        <div className="dash-dims-grid">
          {[
            { label: "Peso (kg)", val: peso, set: setPeso, step: 0.1, min: 0.1 },
            { label: "Largo (cm)", val: largo, set: setLargo, step: 1, min: 1 },
            { label: "Ancho (cm)", val: ancho, set: setAncho, step: 1, min: 1 },
            { label: "Alto (cm)",  val: alto,  set: setAlto,  step: 1, min: 1 },
          ].map(({ label, val, set, step, min }) => (
            <div className="dash-dim-field" key={label}>
              <label className="dash-dim-label">{label}</label>
              <input
                className="dash-dim-input"
                type="number"
                value={val}
                min={min}
                step={step}
                onChange={(e) => set(Number(e.target.value))}
              />
            </div>
          ))}
        </div>
      </div>

      {/* ── LOADING ── */}
      {loading && (
        <div className="dash-loading">
          <div className="dash-loading-inner">
            <div className="dash-loading-orb" />
            <div>
              <p className="dash-loading-title">Analizando mercados globales</p>
              <p className="dash-loading-sub">El agente MarketScan está procesando tendencias en tiempo real…</p>
            </div>
          </div>
          <div className="dash-loading-steps">
            {["Consultando Google Trends", "Identificando mercados top", "Calculando costos logísticos"].map((s, i) => (
              <div className="dash-loading-step" key={s} style={{ animationDelay: `${i * 0.5}s` }}>
                <div className="dash-loading-step-dot" style={{ animationDelay: `${i * 0.5}s` }} />
                <span>{s}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── RESULTADOS ── */}
      {resultados.length > 0 && (
        <div className="dash-results">
          <div className="dash-results-header">
            <div>
              <p className="dash-results-eyebrow">— Resultados del análisis</p>
              <h2 className="dash-results-title">
                Mejores mercados para <em>"{buscado}"</em>
              </h2>
            </div>
            <span className="dash-results-badge">
              <span className="dash-nav-dot" />
              {resultados.length} mercados encontrados
            </span>
          </div>

          <div className="dash-cards">
            {resultados.map((r, i) => (
              <div className="dash-card" key={i} style={{ "--rank-color": rankColor(i) }}>
                <div className="dash-card-rank">
                  <span className="dash-card-rank-num">#{i + 1}</span>
                  <span className="dash-card-rank-label">{rankLabel(i)}</span>
                </div>
                <div className="dash-card-country">
                  <h2 className="dash-card-pais">{r.pais}</h2>
                  <p className="dash-card-ciudad">{r.ciudad}</p>
                </div>
                <div className="dash-card-divider" />
                <div className="dash-card-metrics">
                  <div className="dash-card-metric">
                    <span className="dash-card-metric-label">Distancia</span>
                    <span className="dash-card-metric-val">{r.distancia.toLocaleString()} km</span>
                  </div>
                  <div className="dash-card-metric">
                    <span className="dash-card-metric-label">Peso final</span>
                    <span className="dash-card-metric-val">{r.peso} kg</span>
                  </div>
                </div>
                <div className="dash-card-cost">
                  <span className="dash-card-cost-label">Costo estimado de envío</span>
                  <span className="dash-card-cost-val">${r.costo} <small>USD</small></span>
                </div>
                <div className="dash-card-bar-bg">
                  <div className="dash-card-bar-fill" style={{ width: `${100 - i * 28}%` }} />
                </div>
              </div>
            ))}
          </div>

          {/* ── BOTÓN TRADEADVISOR ── */}
          <div className="dash-ta-cta">
            <div className="dash-ta-cta-info">
              <div className="dash-ta-cta-dot" />
              <div>
                <p className="dash-ta-cta-title">Agente TradeAdvisor disponible</p>
                <p className="dash-ta-cta-sub">
                  Genera una estrategia completa de exportación con precios,
                  canales, requisitos y posicionamiento para cada mercado.
                </p>
              </div>
            </div>
            <button className="dash-ta-btn" onClick={ejecutarTradeAdvisor}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              Ejecutar Agente TradeAdvisor
            </button>
          </div>
        </div>
      )}

      {/* ── EMPTY STATE ── */}
      {!loading && resultados.length === 0 && buscado === "" && (
        <div className="dash-empty">
          <div className="dash-empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9" />
              <path d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20" />
            </svg>
          </div>
          <p className="dash-empty-title">Listo para analizar</p>
          <p className="dash-empty-sub">
            Ingresa un producto y las dimensiones del paquete para descubrir
            los mejores mercados de exportación.
          </p>
        </div>
      )}

      {/* ── FOOTER ── */}
      <footer className="exp-footer" style={{ margin: "4rem 0 0" }}>
        <div>
          <div className="exp-footer-logo">EXPORTIA</div>
          <div className="exp-footer-city">Bucaramanga, Santander · Colombia</div>
        </div>
        <div className="exp-footer-right">
          <a href="mailto:exportia@outlook.com" className="exp-footer-email">exportia@outlook.com</a>
          <div className="exp-footer-copy">+57 314 675 8945</div>
        </div>
      </footer>
    </div>
  );
}
