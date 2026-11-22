"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Header from "../components/Header";
import Footer from "../components/Footer";
import { useAuth } from "@/lib/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setCargando(true);
    try {
      await login(email, password);
      router.push("/perfil");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Error al iniciar sesión. Verifica tus credenciales.");
      }
    } finally {
      setCargando(false);
    }
  }

  function rellenarCuentaPrueba() {
    setEmail("ana@utb.edu.co");
    setPassword("Password123!");
  }

  return (
    <div className="site-shell">
      <Header />

      <main className="auth-page">
        <div className="auth-card">
          <div className="auth-card-header">
            <span className="auth-mark" aria-hidden="true">✳</span>
            <span className="section-kicker">ACCESO DE ESTUDIANTE</span>
            <h1>Bienvenido de nuevo</h1>
            <p>Ingresa a tu cuenta para gestionar tus materiales y aportes.</p>
          </div>

          {error && (
            <div className="message error" role="alert" style={{ marginBottom: 18, padding: 14 }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
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
              <span>Contraseña</span>
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>

            <button type="submit" className="search-button auth-submit-btn" disabled={cargando}>
              {cargando ? "Iniciando sesión..." : "Iniciar sesión"} <span aria-hidden="true">↗</span>
            </button>
          </form>

          <div className="auth-card-footer">
            <p>
              ¿Aún no tienes cuenta?{" "}
              <Link href="/registro" className="auth-link">
                Regístrate aquí
              </Link>
            </p>

            <div className="demo-account-hint">
              <span>¿Quieres probar rápido?</span>
              <button type="button" onClick={rellenarCuentaPrueba} className="demo-fill-btn">
                Usar cuenta de demostración (Ana)
              </button>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
