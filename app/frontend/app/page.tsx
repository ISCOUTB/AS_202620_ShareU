"use client";

import Link from "next/link";
import Header from "./components/Header";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <div className="site-shell">
      <Header />

      <section className="hero">
        <div className="hero-inner">
          <div className="hero-copy">
            <span className="eyebrow">
              <span className="eyebrow-star">✦</span> TU ESPACIO PARA APRENDER EN COMUNIDAD
            </span>
            <h1>
              Aprender es mejor <em>cuando compartimos.</em>
            </h1>
            <p className="hero-description">
              Ese apunte que te falta, el taller que necesitas o la idea que te inspira.
              Encuentra material académico compartido por estudiantes como tú.
            </p>
            <div className="hero-buttons">
              <Link className="hero-cta" href="/explorar">
                Explorar materiales <span aria-hidden="true">↗</span>
              </Link>
              <Link className="hero-secondary-btn" href="/nosotros">
                ¿Qué es ShareU?
              </Link>
            </div>
          </div>

          <div className="hero-art" aria-hidden="true">
            <div className="art-orbit orbit-one" />
            <div className="art-orbit orbit-two" />
            <div className="art-flower flower-one">✿</div>
            <div className="art-flower flower-two">✳</div>
            <div className="art-note note-back">
              <span>✦</span>
              <i></i>
              <i></i>
              <i></i>
            </div>
            <div className="art-note note-front">
              <span className="note-symbol">✎</span>
              <i></i>
              <i></i>
              <i></i>
              <span className="note-badge">★ 5.0</span>
            </div>
            <div className="art-pill">ideas que florecen ✳</div>
          </div>
        </div>

        <div className="hero-bottom">
          <span>HECHO PARA ESTUDIANTES, POR ESTUDIANTES</span>
          <span aria-hidden="true">✳ &nbsp; ✳ &nbsp; ✳</span>
        </div>
      </section>

      <section className="landing-features">
        <div className="landing-features-inner">
          <div className="section-heading">
            <div>
              <span className="section-kicker">¿POR QUÉ SHAREU?</span>
              <h2>
                Tu biblioteca colaborativa, <em>al alcance de todos.</em>
              </h2>
            </div>
            <span className="heading-decoration" aria-hidden="true">✿</span>
          </div>

          <div className="landing-cards-grid">
            <div className="landing-card">
              <div className="landing-card-icon" style={{ background: "var(--spring)" }}>
                <span>✳</span>
              </div>
              <h3>Búsqueda Rápida</h3>
              <p>Filtra por universidad, carrera o materia en una sola solicitud sin rodeos.</p>
              <Link href="/explorar" className="landing-card-link">
                Ir a buscar <span>→</span>
              </Link>
            </div>

            <div className="landing-card">
              <div className="landing-card-icon" style={{ background: "var(--sky)", color: "white" }}>
                <span>✦</span>
              </div>
              <h3>Comparte tu Esfuerzo</h3>
              <p>Sube tus apuntes, parciales y talleres para ayudar a otros estudiantes a pasar la materia.</p>
              <Link href="/perfil" className="landing-card-link">
                Tu perfil de aportes <span>→</span>
              </Link>
            </div>

            <div className="landing-card">
              <div className="landing-card-icon" style={{ background: "var(--coral)" }}>
                <span>✿</span>
              </div>
              <h3>Comunidad Verificada</h3>
              <p>Materiales calificados por compañeros de clase con retroalimentación sincera.</p>
              <Link href="/nosotros" className="landing-card-link">
                Conoce más <span>→</span>
              </Link>
            </div>
          </div>

          <div className="landing-cta-banner">
            <div>
              <span className="section-kicker">COMIENZA AHORA</span>
              <h3>¿Listo para encontrar los mejores apuntes?</h3>
              <p>Accede a cientos de guías y talleres organizados por semestre.</p>
            </div>
            <Link className="hero-cta" href="/explorar">
              Ver todos los materiales <span>↗</span>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
