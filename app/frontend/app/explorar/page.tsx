"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { buscarDocumentos, Documento, Filtros } from "@/lib/api";

const campos: { clave: keyof Filtros; etiqueta: string; ejemplo: string }[] = [
  { clave: "palabra_clave", etiqueta: "¿Qué estás buscando?", ejemplo: "Ej. cálculo, programación, física..." },
  { clave: "universidad", etiqueta: "Universidad", ejemplo: "Todas las universidades" },
  { clave: "carrera", etiqueta: "Carrera", ejemplo: "Todas las carreras" },
  { clave: "materia", etiqueta: "Materia", ejemplo: "Todas las materias" },
  { clave: "tipo", etiqueta: "Tipo de material", ejemplo: "Apuntes, talleres, parciales..." },
];

export default function Explorar() {
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
  const textoResultados = resultados.length === 1 ? "resultado" : "resultados";
  return (
    <div className="site-shell">
      <Header />

      <main className="page-main">
        <section className="search-section" aria-labelledby="search-title">
          <div className="section-heading">
            <div>
              <span className="section-kicker">01 / DESCUBRE</span>
              <h1 id="search-title" className="page-title">
                Explorar <em>materiales académicos.</em>
              </h1>
              <p>Busca por palabra clave o filtra para encontrar justo lo que necesitas.</p>
            </div>
            <span className="heading-decoration" aria-hidden="true">✿</span>
          </div>

          <form onSubmit={onSubmit} className="search-panel">
            <div className="fields-grid">
              {campos.map(({ clave, etiqueta, ejemplo }) => (
                <label className={`field ${clave === "palabra_clave" ? "field-primary" : ""}`} key={clave}>
                  <span>{etiqueta}</span>
                  <input
                    aria-label={etiqueta}
                    placeholder={ejemplo}
                    value={filtros[clave] ?? ""}
                    onChange={(e) => setFiltros((prev) => ({ ...prev, [clave]: e.target.value }))}
                  />
                </label>
              ))}
            </div>
            <div className="search-actions">
              <span>Un mundo de conocimiento, a un clic.</span>
              <div>
                <button className="clear-button" type="button" onClick={limpiar}>
                  Limpiar filtros
                </button>
                <button className="search-button" type="submit" disabled={cargando}>
                  {cargando ? "Buscando..." : "Buscar materiales"} <span aria-hidden="true">↗</span>
                </button>
              </div>
            </div>
          </form>
        </section>

        <section className="results-section" aria-labelledby="results-title">
          <div className="results-heading">
            <div>
              <span className="section-kicker">02 / RESULTADOS</span>
              <h2 id="results-title">
                Materiales para <em>inspirarte.</em>
              </h2>
            </div>
            <span className="result-count" aria-live="polite">
             {cargando ? "Buscando..." : `${resultados.length} ${textoResultados}`}
            </span>
          </div>

          {error && (
            <div className="message error" role="alert">
              {error} <button type="button" onClick={() => void buscar(filtros)}>Reintentar</button>
            </div>
          )}

          {cargando && <div className="message" role="status">Estamos buscando materiales para ti…</div>}

          {!cargando && !error && (
            resultados.length === 0 ? (
              <div className="empty-state">
                <span aria-hidden="true">✿</span>
                <h3>Aún no encontramos coincidencias</h3>
                <p>Prueba con otra palabra clave o cambia los filtros.</p>
                <button type="button" onClick={limpiar}>Ver todos los materiales ↗</button>
              </div>
            ) : (
              <ul className="fichas">
                {resultados.map((d, i) => (
                  <li key={d.id} className="ficha">
                    <div className={`card-art card-art-${i % 4}`} aria-hidden="true">
                      <span className="card-art-icon">{["✳", "✿", "✦", "❋"][i % 4]}</span>
                      <span className="card-art-text">shareU.</span>
                    </div>
                    <div className="card-body">
                      <span className="tipo">{d.tipo}</span>
                      <h3>{d.titulo}</h3>
                      <p className="card-subject">{d.materia}</p>
                      <div className="card-meta">
                        <span>{d.universidad}</span>
                        <span>{d.carrera}</span>
                      </div>
                      <div className="card-footer">
                        <span>Por {d.autor}</span>
                        <span className="rating">★ {d.calificacion.toFixed(1)}</span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )
          )}
        </section>
      </main>

      <Footer />
    </div>
  );
}
