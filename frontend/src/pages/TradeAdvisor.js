import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "../styles.css";

export default function TradeAdvisor() {
  const BACKEND_URL = "https://lannister-production.up.railway.app";
  const nav = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem("token");

  // Datos recibidos desde MarketScan
  const { producto, mercados } = location.state || {};

  const [loading, setLoading] = useState(false);
  const [analisis, setAnalisis] = useState("");
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (!producto || !mercados || mercados.length === 0) {
      nav("/dashboard");
      return;
    }
    if (!token) { nav("/login"); return; }
    generarAnalisis();
    // eslint-disable-next-line
  }, []);

  const generarAnalisis = async () => {
    setLoading(true);
    setError("");
    setAnalisis("");
    try {
      const res = await fetch(`${BACKEND_URL}/analizar`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ producto, mercados }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        setError(data.error || "Error al generar el análisis.");
      } else {
        setAnalisis(data.analisis);
      }
    } catch {
      setError("Error de conexión con el servidor.");
    }
    setLoading(false);
  };

  const rankColor = (i) => ["#1DFFA3", "#5B9CF6", "#A78BFA"][i] || "#E8EFF8";

  // Parsear el análisis en bloques por mercado
  const parsearBloques = (texto) => {
    if (!texto) return [];
    const bloques = texto
      .split(/(?=\n?[1-3]\.\s|\n?#{1,3}\s|\n?(?:Mercado|MERCADO)\s[1-3])/g)
      .filter((b) => b.trim().length > 50);
    return bloques.length >= 2 ? bloques : [texto];
  };

  // Parsear líneas de un bloque en secciones
  const parsearLineas = (texto) => {
    return texto
      .trim()
      .split("\n")
      .filter((l) => l.trim())
      .map((linea) => {
        const esTitulo = linea.match(/^\*\*|^\d\.\s\*\*|^#{1,3}\s/);
        const texto = linea
          .replace(/\*\*/g, "")
          .replace(/^#+\s/, "")
          .replace(/^\d\.\s/, "")
          .trim();
        return { esTitulo: !!esTitulo, texto };
      })
      .filter((l) => l.texto.length > 0);
  };

  const bloques = parsearBloques(analisis);

  return (
    <div className="ta-root">
      <div className="auth-bg-grid" aria-hidden="true" />

      {/* ── NAV ── */}
      <nav className="dash-nav">
        <div className="exp-logo">
          <span className="exp-logo-dot" />
          EXPORTIA
        </div>
        <div className="dash-nav-center">
          <span className="dash-nav-tag" style={{ color: "#A78BFA", background: "rgba(167,139,250,0.07)", borderColor: "rgba(167,139,250,0.2)" }}>
            <span className="dash-nav-dot" style={{ background: "#A78BFA" }} />
            Agente TradeAdvisor
          </span>
        </div>
        <button className="dash-logout" onClick={() => nav("/dashboard")}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
          Volver a MarketScan
        </button>
      </nav>

      {/* ── HERO ── */}
      <div className="ta-hero">
        <div className="ta-hero-left">
          <p className="dash-hero-eyebrow">— Análisis estratégico de exportación</p>
          <h1 className="dash-hero-title" style={{ fontSize: "clamp(1.8rem, 3.5vw, 2.8rem)" }}>
            Estrategia para exportar<br />
            <em>"{producto}"</em>
          </h1>
          <p className="dash-hero-sub">
            El agente TradeAdvisor ha analizado cada mercado identificado por
            MarketScan y genera una hoja de ruta estratégica completa.
          </p>
        </div>

        {/* Resumen de mercados */}
        <div className="ta-mercados-resumen">
          {mercados && mercados.map((m, i) => (
            <button
              key={i}
              className={`ta-mercado-pill${activeTab === i ? " ta-mercado-pill--active" : ""}`}
              style={{ "--pill-color": rankColor(i) }}
              onClick={() => setActiveTab(i)}
            >
              <span className="ta-mercado-pill-num">#{i + 1}</span>
              <span>{m.pais}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── LOADING ── */}
      {loading && (
        <div className="dash-loading ta-loading">
          <div className="dash-loading-inner">
            <div className="dash-loading-orb" style={{ borderTopColor: "#A78BFA", borderColor: "rgba(167,139,250,0.15)" }} />
            <div>
              <p className="dash-loading-title">TradeAdvisor analizando mercados</p>
              <p className="dash-loading-sub">
                Procesando estrategia de exportación para <strong style={{ color: "#E8EFF8" }}>{producto}</strong> en {mercados?.length} mercados…
              </p>
            </div>
          </div>
          <div className="dash-loading-steps">
            {[
              "Evaluando precios de referencia internacionales",
              "Analizando canales de distribución por mercado",
              "Verificando requisitos de entrada y certificaciones",
              "Elaborando estrategia de posicionamiento",
              "Identificando consideraciones culturales y regulatorias",
            ].map((s, i) => (
              <div className="dash-loading-step" key={s} style={{ animationDelay: `${i * 0.6}s` }}>
                <div className="dash-loading-step-dot" style={{ animationDelay: `${i * 0.6}s`, background: "#A78BFA" }} />
                <span>{s}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── ERROR ── */}
      {error && !loading && (
        <div className="dash-results">
          <div className="auth-error" style={{ maxWidth: 760, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>{error}</span>
            <button onClick={generarAnalisis} style={{ background: "none", border: "none", color: "#A78BFA", cursor: "pointer", fontSize: "0.78rem", flexShrink: 0 }}>
              Reintentar →
            </button>
          </div>
        </div>
      )}

      {/* ── ANÁLISIS ── */}
      {!loading && bloques.length > 0 && (
        <div className="ta-content">

          {/* Tabs de navegación */}
          <div className="ta-tabs">
            {mercados.map((m, i) => (
              <button
                key={i}
                className={`ta-tab${activeTab === i ? " ta-tab--active" : ""}`}
                style={{ "--tab-color": rankColor(i) }}
                onClick={() => setActiveTab(i)}
              >
                <span className="ta-tab-num">#{i + 1}</span>
                <span className="ta-tab-pais">{m.pais}</span>
                <span className="ta-tab-ciudad">{m.ciudad}</span>
              </button>
            ))}
          </div>

          {/* Panel activo */}
          {bloques[activeTab] && (
            <div className="ta-panel" style={{ "--panel-color": rankColor(activeTab) }}>

              {/* Métricas del mercado */}
              <div className="ta-panel-metrics">
                <div className="ta-metric">
                  <span className="ta-metric-label">Distancia desde Bucaramanga</span>
                  <span className="ta-metric-val">{mercados[activeTab]?.distancia.toLocaleString()} km</span>
                </div>
                <div className="ta-metric">
                  <span className="ta-metric-label">Costo logístico estimado</span>
                  <span className="ta-metric-val" style={{ color: rankColor(activeTab) }}>${mercados[activeTab]?.costo} USD</span>
                </div>
                <div className="ta-metric">
                  <span className="ta-metric-label">Peso final del envío</span>
                  <span className="ta-metric-val">{mercados[activeTab]?.peso} kg</span>
                </div>
                <div className="ta-metric">
                  <span className="ta-metric-label">Ranking de potencial</span>
                  <span className="ta-metric-val">
                    {["Mayor", "Alto", "Medio"][activeTab] || "—"} potencial
                  </span>
                </div>
              </div>

              {/* Análisis estratégico */}
              <div className="ta-panel-analisis">
                {parsearLineas(bloques[activeTab]).map((linea, j) => (
                  linea.esTitulo
                    ? <h3 key={j} className="ta-section-title">{linea.texto}</h3>
                    : <p key={j} className="ta-section-text">{linea.texto}</p>
                ))}
              </div>
            </div>
          )}

          {/* Acciones */}
          <div className="ta-actions">
            <button className="ta-btn-retry" onClick={generarAnalisis}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/>
              </svg>
              Regenerar análisis
            </button>
            <button className="ta-btn-back" onClick={() => nav("/dashboard")}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
              Nuevo análisis en MarketScan
            </button>
          </div>
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
