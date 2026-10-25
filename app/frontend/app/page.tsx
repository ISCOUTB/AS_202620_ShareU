"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { buscarDocumentos, Documento, Filtros } from "@/lib/api";

export default function Home() {
  const [filtros, setFiltros] = useState<Filtros>({});
  const [resultados, setResultados] = useState<Documento[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  // Número de la última búsqueda lanzada: una respuesta anterior (tardía o repetida) no pisa a la última.
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
    buscar({});
  }, []);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    buscar(filtros);
  }

  const campo = (clave: keyof Filtros, etiqueta: string) => (
    <input
      aria-label={etiqueta}
      placeholder={etiqueta}
      value={filtros[clave] ?? ""}
      onChange={(e) => setFiltros({ ...filtros, [clave]: e.target.value })}
    />
  );

  return (
    <>
      <section className="hero">
        <h1>Encuentra lo que tu compañero ya resolvió.</h1>
        <form onSubmit={onSubmit} className="buscador">
          {campo("palabra_clave", "Palabra clave")}
          {campo("universidad", "Universidad")}
          {campo("carrera", "Carrera")}
          {campo("materia", "Materia")}
          {campo("tipo", "Tipo")}
          <button type="submit">Buscar</button>
        </form>
      </section>
      <main>
        {error && <p className="vacio">{error}</p>}
        {cargando && <p>Buscando…</p>}
        {!cargando && !error && (
          <>
            <h2>{resultados.length} resultado{resultados.length === 1 ? "" : "s"}</h2>
            {resultados.length === 0 ? (
              <p className="vacio">Nada por aquí. Prueba otra palabra clave.</p>
            ) : (
              <ul className="fichas">
                {resultados.map((d) => (
                  <li key={d.id} className="ficha">
                    <span className="tipo">{d.tipo}</span>
                    <strong>{d.titulo}</strong>
                    <span>{d.universidad} · {d.carrera} · {d.materia}</span>
                    <span>por {d.autor} — ★ {d.calificacion.toFixed(1)}</span>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </main>
    </>
  );
}
