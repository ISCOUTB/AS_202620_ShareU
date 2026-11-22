"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function Header() {
  const pathname = usePathname();
  const { usuario, logout } = useAuth();

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link className="brand" href="/" aria-label="ShareU, ir al inicio">
          <span className="brand-mark" aria-hidden="true">✳</span>
          <span>
            share<span className="brand-u">U</span>
            <span className="brand-dot">.</span>
          </span>
        </Link>

        <nav className="site-nav" aria-label="Navegación principal">
          <Link
            href="/"
            className={pathname === "/" ? "nav-active" : ""}
          >
            Inicio
          </Link>
          <Link
            href="/explorar"
            className={pathname === "/explorar" ? "nav-active" : ""}
          >
            Explorar materiales
          </Link>
          <Link
            href="/nosotros"
            className={pathname === "/nosotros" ? "nav-active" : ""}
          >
            ¿Qué es ShareU?
          </Link>
        </nav>

        <div className="header-auth">
          {usuario ? (
            <div className="user-badge-group">
              <Link
                href="/perfil"
                className={`header-link user-pill ${pathname === "/perfil" ? "nav-active" : ""}`}
              >
                <span className="user-avatar" aria-hidden="true">
                  {usuario.nombre.charAt(0).toUpperCase()}
                </span>
                <span>{usuario.nombre}</span>
              </Link>
              <button
                type="button"
                className="header-logout-btn"
                onClick={() => void logout()}
                title="Cerrar sesión"
              >
                Salir
              </button>
            </div>
          ) : (
            <div className="guest-nav-actions">
              <Link
                className={`header-link ${pathname === "/login" ? "nav-active" : ""}`}
                href="/login"
              >
                Iniciar sesión <span aria-hidden="true">↗</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
