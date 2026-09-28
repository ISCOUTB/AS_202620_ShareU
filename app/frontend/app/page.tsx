"use client";

import { FormEvent, useEffect, useState } from "react";
import { buscarDocumentos, Documento, Filtros } from "@/lib/api";

export default function Home() {
  const [filtros, setFiltros] = useState<Filtros>({});
  const [resultados, setResultados] = useState<Documento[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  async function buscar(f: Filtros) {
    setCargando(true);
    setError(null);
    try {
      const data = await buscarDocumentos(f);
      setResultados(data.resultados);
    } catch {
      setError("No se pudo conectar con el backend.");
    } finally {
      setCargando(false);
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
