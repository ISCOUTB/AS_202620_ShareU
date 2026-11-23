"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Usuario,
  loginUsuario,
  registrarUsuario,
  obtenerPerfil,
  cerrarSesion,
} from "./api";

interface AuthContextType {
  usuario: Usuario | null;
  token: string | null;
  cargando: boolean;
  login: (email: string, pass: string) => Promise<void>;
  registro: (datos: {
    email: string;
    password: string;
    nombre: string;
    universidad?: string;
    carrera?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  recargarPerfil: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  usuario: null,
  token: null,
  cargando: true,
  login: async () => {},
  registro: async () => {},
  logout: async () => {},
  recargarPerfil: async () => {},
});

const STORAGE_TOKEN_KEY = "shareu_token";
const STORAGE_USER_KEY = "shareu_usuario";

export function AuthProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    try {
      const guardadoToken = localStorage.getItem(STORAGE_TOKEN_KEY);
      const guardadoUser = localStorage.getItem(STORAGE_USER_KEY);
      if (guardadoToken && guardadoUser) {
        setToken(guardadoToken);
        setUsuario(JSON.parse(guardadoUser));
        // Validar token en segundo plano
        obtenerPerfil(guardadoToken)
          .then((perfilActualizado) => {
            setUsuario(perfilActualizado);
            localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(perfilActualizado));
          })
          .catch(() => {
            // Token expirado o inválido
            localStorage.removeItem(STORAGE_TOKEN_KEY);
            localStorage.removeItem(STORAGE_USER_KEY);
            setToken(null);
            setUsuario(null);
          });
      }
    } catch {
      // Ignorar errores de localStorage
    } finally {
      setCargando(false);
    }
  }, []);

  const login = useCallback(async (email: string, pass: string) => {
    const respuesta = await loginUsuario(email, pass);
    setToken(respuesta.token);
    setUsuario(respuesta.usuario);
    try {
      localStorage.setItem(STORAGE_TOKEN_KEY, respuesta.token);
      localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(respuesta.usuario));
    } catch {}
  }, []);

  const registro = useCallback(async (datos: {
    email: string;
    password: string;
    nombre: string;
    universidad?: string;
    carrera?: string;
  }) => {
    await registrarUsuario(datos);
    // Iniciar sesión automáticamente tras registro
    await login(datos.email, datos.password);
  }, [login]);

  const logout = useCallback(async () => {
    if (token) {
      await cerrarSesion(token);
    }
    setToken(null);
    setUsuario(null);
    try {
      localStorage.removeItem(STORAGE_TOKEN_KEY);
      localStorage.removeItem(STORAGE_USER_KEY);
    } catch {}
  }, [token]);

  const recargarPerfil = useCallback(async () => {
    if (!token) return;
    try {
      const perfilActualizado = await obtenerPerfil(token);
      setUsuario(perfilActualizado);
      localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(perfilActualizado));
    } catch {}
  }, [token]);

  const contextValue = useMemo<AuthContextType>(
    () => ({ usuario, token, cargando, login, registro, logout, recargarPerfil }),
    [usuario, token, cargando, login, registro, logout, recargarPerfil]
  );

  return (
    <AuthContext.Provider
      value={contextValue}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
