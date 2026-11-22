"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { buscarDocumentos, Documento, Filtros } from "@/lib/api";

const campos: { clave: keyof Filtros; etiqueta: string; ejemplo: string }[] = [
  { clave: "palabra_clave", etiqueta: "¿Qué estás buscando?", ejemplo: "Ej. cálculo, programación, física..." },
  { clave: "universidad", etiqueta: "Universidad", ejemplo: "Todas las universidades" },
  { clave: "carrera", etiqueta: "Carrera", ejemplo: "Todas las carreras" },
  { clave: "materia", etiqueta: "Materia", ejemplo: "Todas las materias" },
  { clave: "tipo", etiqueta: "Tipo de material", ejemplo: "Apuntes, talleres, parciales..." },
];

export default function Home() {
  const [filtros, setFiltros] = useState<Filtros>({});
  const [resultados, setResultados] = useState<Documento[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const ultimaBusqueda = useRef(0);

  async function buscar(f: Filtros) {
    const id = ++ultimaBusqueda.current;
    setCargando(true);
    setError(null);
    try {
      const data = await buscarDocumentos(f);
      if (id === ultimaBusqueda.current) setResultados(data.resultados);
    } catch {
      if (id === ultimaBusqueda.current) {
        setError("No se pudo conectar con el backend o tardó demasiado. Intenta de nuevo.");
      }
    } finally {
      if (id === ultimaBusqueda.current) setCargando(false);
    }
  }

  useEffect(() => {
    void buscar({});
  }, []);

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    void buscar(filtros);
  }

  function limpiar() {
    setFiltros({});
    void buscar({});
  }

  return (
    <div className="site-shell">
      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="#inicio" aria-label="ShareU, ir al inicio">
            <span className="brand-mark" aria-hidden="true">✳</span>
            <span>share<span className="brand-u">U</span><span className="brand-dot">.</span></span>
          </a>
          <nav className="site-nav" aria-label="Navegación principal">
            <a href="#explorar">Explorar materiales</a>
            <a href="#como-funciona">¿Qué es ShareU?</a>
          </nav>
          <a className="header-link" href="#explorar">Encuentra tu material <span aria-hidden="true">↗</span></a>
        </div>
      </header>

      <section className="hero" id="inicio">
        <div className="hero-inner">
          <div className="hero-copy">
            <span className="eyebrow"><span className="eyebrow-star">✦</span> TU ESPACIO PARA APRENDER EN COMUNIDAD</span>
            <h1>Aprender es mejor <em>cuando compartimos.</em></h1>
            <p className="hero-description">Ese apunte que te falta, el taller que necesitas o la idea que te inspira. Encuentra material académico compartido por estudiantes como tú.</p>
            <a className="hero-cta" href="#explorar">Explorar materiales <span aria-hidden="true">↗</span></a>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="art-orbit orbit-one" />
            <div className="art-orbit orbit-two" />
            <div className="art-flower flower-one">✿</div>
            <div className="art-flower flower-two">✳</div>
            <div className="art-note note-back"><span>✦</span><i></i><i></i><i></i></div>
            <div className="art-note note-front"><span className="note-symbol">✎</span><i></i><i></i><i></i><span className="note-badge">★ 5.0</span></div>
            <div className="art-pill">ideas que florecen ✳</div>
          </div>
        </div>
        <div className="hero-bottom"><span>HECHO PARA ESTUDIANTES, POR ESTUDIANTES</span><span aria-hidden="true">✳ &nbsp; ✳ &nbsp; ✳</span></div>
      </section>

      <main id="explorar">
        <section className="search-section" aria-labelledby="search-title">
          <div className="section-heading">
            <div><span className="section-kicker">01 / DESCUBRE</span><h2 id="search-title">Tu próximo <em>gran hallazgo.</em></h2><p>Busca por palabra clave o filtra para encontrar justo lo que necesitas.</p></div>
            <span className="heading-decoration" aria-hidden="true">✿</span>
          </div>
          <form onSubmit={onSubmit} className="search-panel">
            <div className="fields-grid">
              {campos.map(({ clave, etiqueta, ejemplo }) => (
                <label className={`field ${clave === "palabra_clave" ? "field-primary" : ""}`} key={clave}>
                  <span>{etiqueta}</span>
                  <input aria-label={etiqueta} placeholder={ejemplo} value={filtros[clave] ?? ""} onChange={(e) => setFiltros((prev) => ({ ...prev, [clave]: e.target.value }))} />
                </label>
              ))}
            </div>
            <div className="search-actions"><span>Un mundo de conocimiento, a un clic.</span><div><button className="clear-button" type="button" onClick={limpiar}>Limpiar filtros</button><button className="search-button" type="submit" disabled={cargando}>{cargando ? "Buscando..." : "Buscar materiales"} <span aria-hidden="true">↗</span></button></div></div>
          </form>
        </section>

        <section className="results-section" aria-labelledby="results-title">
          <div className="results-heading"><div><span className="section-kicker">02 / EXPLORA</span><h2 id="results-title">Materiales para <em>inspirarte.</em></h2></div><span className="result-count" aria-live="polite">{cargando ? "Buscando..." : `${resultados.length} resultado${resultados.length === 1 ? "" : "s"}`}</span></div>
          {error && <div className="message error" role="alert">{error} <button type="button" onClick={() => void buscar(filtros)}>Reintentar</button></div>}
          {cargando && <div className="message" role="status">Estamos buscando materiales para ti…</div>}
          {!cargando && !error && (resultados.length === 0 ? <div className="empty-state"><span aria-hidden="true">✿</span><h3>Aún no encontramos coincidencias</h3><p>Prueba con otra palabra clave o cambia los filtros.</p><button type="button" onClick={limpiar}>Ver todos los materiales ↗</button></div> : <ul className="fichas">{resultados.map((d, i) => <li key={d.id} className="ficha"><div className={`card-art card-art-${i % 4}`} aria-hidden="true"><span className="card-art-icon">{["✳", "✿", "✦", "❋"][i % 4]}</span><span className="card-art-text">shareU.</span></div><div className="card-body"><span className="tipo">{d.tipo}</span><h3>{d.titulo}</h3><p className="card-subject">{d.materia}</p><div className="card-meta"><span>{d.universidad}</span><span>{d.carrera}</span></div><div className="card-footer"><span>Por {d.autor}</span><span className="rating">★ {d.calificacion.toFixed(1)}</span></div></div></li>)}</ul>)}
        </section>
      </main>

      <section className="about-strip" id="como-funciona"><span className="about-symbol" aria-hidden="true">✳</span><div><span className="section-kicker">UN POCO SOBRE NOSOTROS</span><h2>El conocimiento crece <em>cuando se comparte.</em></h2><p>ShareU conecta estudiantes a través de recursos académicos. Explora, descubre y sigue aprendiendo.</p></div></section>
      <footer className="site-footer"><a className="footer-brand" href="#inicio">shareU<span>.</span></a><span>Un espacio para aprender juntos.</span><span>Hecho con ✿ para la comunidad estudiantil</span></footer>
    </div>
  );
}
