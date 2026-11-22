"use client";

import Link from "next/link";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function Nosotros() {
  return (
    <div className="site-shell">
      <Header />

      <section className="about-hero-section">
        <div className="about-hero-inner">
          <span className="eyebrow">
            <span className="eyebrow-star">✦</span> NUESTRA HISTORIA Y MISIÓN
          </span>
          <h1 className="about-title">
            El conocimiento crece <em>cuando se comparte.</em>
          </h1>
          <p className="about-lead">
            ShareU nació con una idea sencilla: ningún estudiante debería quedarse atrás por no tener acceso
            a buenos apuntes, guías claras o exámenes anteriores para prepararse.
          </p>
        </div>
      </section>

      <section className="about-content-section">
        <div className="about-content-inner">
          <div className="about-grid">
            <div className="about-card-featured">
              <span className="about-card-badge">NUESTRA VISIÓN</span>
              <h2>Democratizar el aprendizaje universitario</h2>
              <p>
                Creemos en un entorno académico donde el esfuerzo colaborativo potencia a cada estudiante.
                ShareU conecta a estudiantes de diferentes facultades y universidades para intercambiar
                materiales de alta calidad y retroalimentación constructiva.
              </p>
              <div className="about-stats-row">
                <div className="about-stat">
                  <strong>100%</strong>
                  <span>Acceso libre</span>
                </div>
                <div className="about-stat">
                  <strong>+5</strong>
                  <span>Universidades</span>
                </div>
                <div className="about-stat">
                  <strong>★ 4.8</strong>
                  <span>Calificación promedio</span>
                </div>
              </div>
            </div>

            <div className="about-card-side">
              <div className="about-side-box" style={{ background: "var(--spring)" }}>
                <span className="side-box-icon">✳</span>
                <h3>Sin muros de pago</h3>
                <p>Todos los recursos están disponibles de manera abierta y gratuita para la comunidad.</p>
              </div>
              <div className="about-side-box" style={{ background: "var(--rose)" }}>
                <span className="side-box-icon">✿</span>
                <h3>Organizado por materia</h3>
                <p>Fácil de buscar y filtrar sin perder tiempo navegando entre carpetas desordenadas.</p>
              </div>
            </div>
          </div>

          <div className="about-steps-section">
            <div className="section-heading">
              <div>
                <span className="section-kicker">¿CÓMO FUNCIONA?</span>
                <h2>
                  Tres pasos para <em>aprender juntos.</em>
                </h2>
              </div>
            </div>

            <div className="steps-container">
              <div className="step-item">
                <span className="step-num">01</span>
                <h3>Explora y Descubre</h3>
                <p>Usa nuestro motor de búsqueda para encontrar resúmenes, talleres resueltos y guías de estudio.</p>
              </div>
              <div className="step-item">
                <span className="step-num">02</span>
                <h3>Aprende y Evalúa</h3>
                <p>Descarga o lee el material y califica su utilidad para ayudar a otros compañeros.</p>
              </div>
              <div className="step-item">
                <span className="step-num">03</span>
                <h3>Comparte tus Apuntes</h3>
                <p>Crea tu cuenta, sube tus notas desde tu perfil y ayuda a hacer crecer la biblioteca común.</p>
              </div>
            </div>
          </div>

          <div className="about-cta-box">
            <span className="about-symbol" aria-hidden="true">✳</span>
            <div>
              <h2>¿Listo para unirte a ShareU?</h2>
              <p>Empieza a explorar el material académico o crea tu cuenta para subir tus propios aportes.</p>
              <div className="about-cta-actions">
                <Link className="hero-cta" href="/explorar">
                  Explorar materiales <span>↗</span>
                </Link>
                <Link className="header-link" href="/registro">
                  Crear cuenta gratis <span>↗</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
