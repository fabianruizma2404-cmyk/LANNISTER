import { useNavigate } from "react-router-dom";
import "../styles.css";

export default function Home() {
  const nav = useNavigate();

  return (
    <div>
      <header className="hero">
        <h1>🌍 EXPORTIA</h1>
        <p>Soluciones inteligentes para exportación global</p>

        <div className="buttons">
          <button onClick={() => nav("/login")}>Iniciar sesión</button>
          <button onClick={() => nav("/registro")}>Registrarse</button>
        </div>
      </header>

      <section className="services">
        <h2>Servicios</h2>

        <div className="card">
          <h3>📦 Logística Internacional</h3>
          <p>Optimización de envíos globales</p>
        </div>

        <div className="card">
          <h3>📊 Inteligencia de mercados</h3>
          <p>Análisis con IA y tendencias</p>
        </div>

        <div className="card">
          <h3>🤝 Consultoría</h3>
          <p>Estrategia para exportación</p>
        </div>
      </section>

      <footer>
        <h3>Exportia</h3>
        <p>Bucaramanga, Santander</p>
        <p>exportia@outlook.com</p>
      </footer>
    </div>
  );
}
