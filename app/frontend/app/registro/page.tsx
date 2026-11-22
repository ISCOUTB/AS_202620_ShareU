"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { useAuth } from "@/lib/auth";

export default function Registro() {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [universidad, setUniversidad] = useState("Universidad Tecnológica de Bolívar");
  const [carrera, setCarrera] = useState("Ingeniería de Sistemas");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const { registro } = useAuth();
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setCargando(true);
    try {
      await registro({
        nombre,
        email,
        password,
        universidad,
        carrera,
      });
      router.push("/perfil");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Error al crear la cuenta. Por favor intenta de nuevo.");
      }
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="site-shell">
      <Header />

      <main className="auth-page">
        <div className="auth-card">
          <div className="auth-card-header">
            <span className="auth-mark" aria-hidden="true" style={{ background: "var(--coral)" }}>
              ✿
            </span>
            <span className="section-kicker">ÚNETE A LA COMUNIDAD</span>
            <h1>Crear una cuenta</h1>
            <p>Comienza a compartir tus notas y acceder a material de estudio.</p>
          </div>

          {error && (
            <div className="message error" role="alert" style={{ marginBottom: 18, padding: 14 }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <label className="field">
              <span>Nombre y Apellido</span>
              <input
                type="text"
                required
                placeholder="Ej. Dayana Narváez"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
              />
            </label>

            <label className="field">
              <span>Correo electrónico</span>
              <input
                type="email"
                required
                placeholder="tu.correo@utb.edu.co"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>

            <label className="field">
              <span>Contraseña (mínimo 6 caracteres)</span>
              <input
                type="password"
                required
                minLength={6}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>

            <div className="auth-row-2">
              <label className="field">
                <span>Universidad</span>
                <input
                  type="text"
                  required
                  placeholder="Tu universidad"
                  value={universidad}
                  onChange={(e) => setUniversidad(e.target.value)}
                />
              </label>

              <label className="field">
                <span>Carrera</span>
                <input
                  type="text"
                  required
                  placeholder="Tu carrera"
                  value={carrera}
                  onChange={(e) => setCarrera(e.target.value)}
                />
              </label>
            </div>

            <button type="submit" className="search-button auth-submit-btn" disabled={cargando}>
              {cargando ? "Creando cuenta..." : "Registrarme"} <span aria-hidden="true">↗</span>
            </button>
          </form>

          <div className="auth-card-footer">
            <p>
              ¿Ya tienes cuenta?{" "}
              <Link href="/login" className="auth-link">
                Inicia sesión aquí
              </Link>
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
