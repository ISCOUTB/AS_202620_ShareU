"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { useAuth } from "@/lib/auth";
import {
  Documento,
  obtenerDocumentosUsuario,
  subirDocumentoUsuario,
} from "@/lib/api";

const TIPOS_MATERIAL = [
  "Apuntes",
  "Taller",
  "Parcial",
  "Guía de Estudio",
  "Resumen",
  "Ejercicios Resueltos",
];

export default function Perfil() {
  const { usuario, token, cargando: authCargando, logout } = useAuth();
  const [documentos, setDocumentos] = useState<Documento[]>([]);
  const [cargandoDocs, setCargandoDocs] = useState(false);
  const [errorDocs, setErrorDocs] = useState<string | null>(null);

  // Estado para el modal/panel de subida de material
  const [mostrarModal, setMostrarModal] = useState(false);
  const [subiendo, setSubiendo] = useState(false);
  const [errorSubida, setErrorSubida] = useState<string | null>(null);
  const [exitoSubida, setExitoSubida] = useState(false);

  // Campos del formulario
  const [titulo, setTitulo] = useState("");
  const [materia, setMateria] = useState("");
  const [tipo, setTipo] = useState("Apuntes");
  const [palabrasClave, setPalabrasClave] = useState("");

  useEffect(() => {
    if (!token || !usuario) return;

    setCargandoDocs(true);
    setErrorDocs(null);
    obtenerDocumentosUsuario(token)
      .then((docs) => setDocumentos(docs))
      .catch((err) => setErrorDocs(err.message || "Error al cargar tus materiales"))
      .finally(() => setCargandoDocs(false));
  }, [token, usuario]);

  async function handleSubirMaterial(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token || !usuario) return;

    setSubiendo(true);
    setErrorSubida(null);
    setExitoSubida(false);

    try {
      const nuevoDoc = await subirDocumentoUsuario(token, {
        titulo: titulo.trim(),
        materia: materia.trim(),
        tipo,
        universidad: usuario.universidad,
        carrera: usuario.carrera,
        palabras_clave: palabrasClave.trim(),
      });

      setDocumentos((prev) => [nuevoDoc, ...prev]);
      setExitoSubida(true);
      setTitulo("");
      setMateria("");
      setPalabrasClave("");
      setTimeout(() => {
        setMostrarModal(false);
        setExitoSubida(false);
      }, 1200);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorSubida(err.message);
      } else {
        setErrorSubida("Error al subir el material. Intenta de nuevo.");
      }
    } finally {
      setSubiendo(false);
    }
  }

  if (authCargando) {
    return (
      <div className="site-shell">
        <Header />
        <main className="page-main">
          <div className="message" role="status">
            Cargando tu perfil...
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!usuario) {
    return (
      <div className="site-shell">
        <Header />
        <main className="page-main">
          <div className="empty-state auth-required-box">
            <span aria-hidden="true">🔒</span>
            <h2>Inicia sesión para ver tu perfil</h2>
            <p>Necesitas una cuenta de estudiante para gestionar y publicar materiales.</p>
            <div className="auth-prompt-actions">
              <Link href="/login" className="hero-cta">
                Iniciar sesión <span>↗</span>
              </Link>
              <Link href="/registro" className="header-link">
                Crear cuenta gratis
              </Link>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="site-shell">
      <Header />

      <main className="profile-main">
        {/* Banner de perfil */}
        <section className="profile-header-card">
          <div className="profile-header-top">
            <div className="profile-avatar-large">
              <span>{usuario.nombre.charAt(0).toUpperCase()}</span>
            </div>
            <div className="profile-user-info">
              <div className="profile-name-row">
                <h1>{usuario.nombre}</h1>
                <span className="profile-verified-badge" title="Estudiante verificado">
                  ✓ Verificado
                </span>
              </div>
              <p className="profile-email">{usuario.email}</p>
              <div className="profile-tags">
                <span className="profile-pill">{usuario.universidad}</span>
                <span className="profile-pill">{usuario.carrera}</span>
                <span className="profile-pill pill-counter">
                  📚 {documentos.length} aporte{documentos.length === 1 ? "" : "s"}
                </span>
              </div>
            </div>

            <div className="profile-header-actions">
              <button
                type="button"
                className="hero-cta upload-btn"
                onClick={() => setMostrarModal(true)}
              >
                <span>➕</span> Subir material
              </button>
              <button
                type="button"
                className="clear-button profile-logout-btn"
                onClick={() => void logout()}
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </section>

        {/* Modal de subida de material */}
        {mostrarModal && (
          <div className="modal-overlay">
  <button
    type="button"
    className="modal-backdrop"
    aria-label="Cerrar ventana de subida de material"
    onClick={() => setMostrarModal(false)}
  />
  <div
    className="modal-dialog"
    role="dialog"
    aria-modal="true"
    aria-label="Subir nuevo material"
  >
              <div className="modal-header">
                <div>
                  <span className="section-kicker">COMPARTE TU CONOCIMIENTO</span>
                  <h2>Subir nuevo material</h2>
                </div>
                <button
                  type="button"
                  className="modal-close-btn"
                  onClick={() => setMostrarModal(false)}
                  aria-label="Cerrar ventana"
                >
                  ✕
                </button>
              </div>

              {errorSubida && (
                <div className="message error" style={{ marginBottom: 16, padding: 12 }}>
                  {errorSubida}
                </div>
              )}

              {exitoSubida && (
                <div
                  className="message"
                  style={{
                    background: "var(--spring)",
                    color: "var(--forest)",
                    marginBottom: 16,
                    padding: 12,
                    fontWeight: 700,
                  }}
                >
                  ¡Material publicado exitosamente! ✿
                </div>
              )}

              <form onSubmit={handleSubirMaterial} className="upload-form">
                <label className="field">
                  <span>Título del material *</span>
                  <input
                    type="text"
                    required
                    placeholder="Ej. Taller resuelto de Circuitos I"
                    value={titulo}
                    onChange={(e) => setTitulo(e.target.value)}
                  />
                </label>

                <div className="fields-grid-2">
                  <label className="field">
                    <span>Materia *</span>
                    <input
                      type="text"
                      required
                      placeholder="Ej. Física Mecánica"
                      value={materia}
                      onChange={(e) => setMateria(e.target.value)}
                    />
                  </label>

                  <label className="field">
                    <span>Tipo de material *</span>
                    <select
                      className="field-select"
                      value={tipo}
                      onChange={(e) => setTipo(e.target.value)}
                    >
                      {TIPOS_MATERIAL.map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>

                <label className="field">
                  <span>Palabras clave o temas (opcional)</span>
                  <input
                    type="text"
                    placeholder="Ej. leyes de newton, cinemática, vectores"
                    value={palabrasClave}
                    onChange={(e) => setPalabrasClave(e.target.value)}
                  />
                </label>

                <div className="modal-footer-actions">
                  <button
                    type="button"
                    className="clear-button"
                    onClick={() => setMostrarModal(false)}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="search-button"
                    disabled={subiendo || exitoSubida}
                  >
                    {subiendo ? "Publicando..." : "Publicar material"} <span aria-hidden="true">↗</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Sección de materiales estilo Pinterest (Masonry) */}
        <section className="profile-documents-section">
          <div className="results-heading">
            <div>
              <span className="section-kicker">TABLERO DE APORTES</span>
              <h2>
                Tus materiales <em>compartidos.</em>
              </h2>
            </div>
            <span className="result-count">
              {cargandoDocs
                ? "Cargando..."
                : `${documentos.length} documento${documentos.length === 1 ? "" : "s"}`}
            </span>
          </div>

          {errorDocs && (
            <div className="message error" role="alert">
              {errorDocs}
            </div>
          )}

          {cargandoDocs && (
            <div className="message" role="status">
              Cargando tus materiales...
            </div>
          )}

          {!cargandoDocs && !errorDocs && documentos.length === 0 && (
            <div className="empty-state">
              <span aria-hidden="true">✿</span>
              <h3>Todavía no has compartido materiales</h3>
              <p>
                Sube apuntes de tus clases o talleres para ayudar a la comunidad y empezar a armar tu
                tablero de estudio.
              </p>
              <button
                type="button"
                className="hero-cta"
                onClick={() => setMostrarModal(true)}
                style={{ marginTop: 15 }}
              >
                <span>➕</span> Subir tu primer apunte
              </button>
            </div>
          )}

          {/* Grilla Masonry estilo Pinterest */}
          {!cargandoDocs && documentos.length > 0 && (
            <div className="pinterest-masonry">
              {documentos.map((doc, idx) => {
                const coloresArte = ["#A7D460", "#EABDBB", "#7C79DF", "#F49C92"];
                const iconArte = ["✳", "✿", "✦", "❋"][idx % 4];
                const colorFondo = coloresArte[idx % coloresArte.length];
                const alturaRandom = [160, 200, 140, 180][idx % 4];

                return (
                  <div key={doc.id} className="pinterest-pin">
                    <div
                      className="pin-cover"
                      style={{
                        backgroundColor: colorFondo,
                        height: `${alturaRandom}px`,
                      }}
                    >
                      <span className="pin-cover-icon">{iconArte}</span>
                      <span className="pin-type-tag">{doc.tipo}</span>
                      <span className="pin-brand-watermark">shareU.</span>
                    </div>

                    <div className="pin-content">
                      <div className="pin-rating-row">
                        <span className="rating">★ {doc.calificacion.toFixed(1)}</span>
                        <span className="pin-subject">{doc.materia}</span>
                      </div>

                      <h3 className="pin-title">{doc.titulo}</h3>

                      <div className="pin-details">
                        <span>{doc.universidad}</span>
                        <span>{doc.carrera}</span>
                      </div>

                      <div className="pin-footer">
                        <span className="pin-author">Por ti ({doc.autor})</span>
                        <span className="pin-action-icon" title="Ver recurso">
                          ↗
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>

      <Footer />
    </div>
  );
}
