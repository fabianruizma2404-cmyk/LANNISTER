import { useNavigate } from "react-router-dom";
import "../styles.css";

export default function Home() {
  const nav = useNavigate();

  const services = [
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="9" />
          <path d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20" />
        </svg>
      ),
      title: "Logística Internacional",
      desc: "Optimización de rutas, seguimiento en tiempo real y coordinación con operadores globales.",
      tag: "Activo",
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
      ),
      title: "Inteligencia de Mercados",
      desc: "Análisis predictivo con IA sobre tendencias, demanda y potencial de productos en destinos clave.",
      tag: "IA avanzada",
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
        </svg>
      ),
      title: "Documentos Automáticos",
      desc: "Generación inteligente de facturas, packing lists, certificados de origen y declaraciones aduaneras.",
      tag: "Automático",
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" />
        </svg>
      ),
      title: "Consultoría Especializada",
      desc: "Estrategia de entrada a mercados, negociación y alianzas con agentes internacionales.",
      tag: "Premium",
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="3" width="20" height="14" rx="2" />
          <path d="M8 21h8M12 17v4" />
        </svg>
      ),
      title: "Dashboard en Tiempo Real",
      desc: "Monitoreo de operaciones, alertas de mercado y KPIs de exportación en un solo lugar.",
      tag: "En vivo",
    },
    {
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      ),
      title: "Cumplimiento Normativo",
      desc: "Validación automática de regulaciones aduaneras, aranceles y tratados comerciales vigentes.",
      tag: "Verificado",
    },
  ];

  const agents = [
    {
      name: "Agente DocGen",
      desc: "Genera automáticamente todos los documentos de exportación: facturas, BL, certificados de origen y declaraciones aduaneras con datos validados.",
    },
    {
      name: "Agente MarketScan",
      desc: "Analiza en tiempo real la potencialidad de tu producto en más de 180 mercados: precios, competencia, barreras de entrada y canales de distribución.",
    },
    {
      name: "Agente TradeAdvisor",
      desc: "Asistente experto en comercio exterior. Responde sobre aranceles, incoterms, tratados y estrategias de acercamiento a compradores internacionales.",
    },
    {
      name: "Agente LogiRoute",
      desc: "Optimiza rutas de envío, compara operadores logísticos, calcula costos totales y coordina el seguimiento de carga en tránsito.",
    },
  ];

  return (
    <div className="exp-root">
      {/* Background grid */}
      <div className="exp-bg-grid" aria-hidden="true" />

      {/* NAV */}
      <nav className="exp-nav">
        <div className="exp-logo">
          <span className="exp-logo-dot" />
          EXPORTIA
        </div>
        <ul className="exp-nav-links">
          <li>Servicios</li>
          <li>Mercados</li>
          <li>Agentes IA</li>
          <li>Nosotros</li>
        </ul>
        <div className="exp-nav-cta">
          <button className="btn-ghost" onClick={() => nav("/login")}>
            Iniciar sesión
          </button>
          <button className="btn-solid" onClick={() => nav("/registro")}>
            Registrarse
          </button>
        </div>
      </nav>

      {/* HERO */}
      <div className="exp-hero">
        <div className="exp-tag">
          <span className="exp-tag-dot" />
          Plataforma activa · Colombia &amp; mundo
        </div>
        <h1 className="exp-h1">
          Exporta con la potencia<br />
          de la <em>inteligencia</em> artificial
        </h1>
        <p className="exp-sub">
          Análisis de mercados globales, generación de documentos de exportación
          y asistencia especializada impulsados por agentes de IA.
        </p>
        <div className="exp-cta-row">
          <button className="btn-hero" onClick={() => nav("/registro")}>
            Comenzar ahora
          </button>
          <button className="btn-hero-ghost" onClick={() => nav("/login")}>
            Ver demo
          </button>
        </div>
      </div>

      {/* STATS */}
      <div className="exp-stats">
        <div className="exp-stat">
          <div className="exp-stat-num">180+</div>
          <div className="exp-stat-label">Mercados analizados</div>
        </div>
        <div className="exp-stat">
          <div className="exp-stat-num">98%</div>
          <div className="exp-stat-label">Precisión documental</div>
        </div>
        <div className="exp-stat">
          <div className="exp-stat-num">3×</div>
          <div className="exp-stat-label">Velocidad de exportación</div>
        </div>
      </div>

      {/* SERVICES */}
      <section className="exp-section" id="servicios">
        <p className="exp-section-tag">— Servicios</p>
        <h2 className="exp-section-title">
          Todo lo que necesitas<br />para exportar con éxito
        </h2>
        <div className="exp-services">
          {services.map((s) => (
            <div className="exp-svc" key={s.title}>
              <div className="exp-svc-icon">{s.icon}</div>
              <h3>{s.title}</h3>
              <p>{s.desc}</p>
              <span className="exp-svc-tag">{s.tag}</span>
            </div>
          ))}
        </div>
      </section>

      {/* AGENTS */}
      <section className="exp-section" id="agentes">
        <p className="exp-section-tag">— Agentes IA</p>
        <h2 className="exp-section-title">
          Agentes especializados<br />trabajando por ti
        </h2>
        <div className="exp-agents">
          {agents.map((a) => (
            <div className="exp-agent" key={a.name}>
              <div className="exp-agent-header">
                <div className="exp-agent-badge" />
                <span className="exp-agent-name">{a.name}</span>
                <span className="exp-agent-status">EN LÍNEA</span>
              </div>
              <p>{a.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="exp-footer">
        <div>
          <div className="exp-footer-logo">EXPORTIA</div>
          <div className="exp-footer-city">Bucaramanga, Santander · Colombia</div>
        </div>
        <div className="exp-footer-right">
          <a href="mailto:exportia@outlook.com" className="exp-footer-email">
            exportia@outlook.com
          </a>
          <div className="exp-footer-copy">
            © 2025 Exportia. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </div>
  );
}
