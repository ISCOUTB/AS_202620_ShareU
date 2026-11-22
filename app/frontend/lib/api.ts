export type Documento = {
  id: number;
  titulo: string;
  universidad: string;
  carrera: string;
  materia: string;
  tipo: string;
  autor: string;
  calificacion: number;
  palabras_clave?: string;
};

export type ResultadoBusqueda = { total: number; resultados: Documento[] };

export type Filtros = {
  palabra_clave?: string;
  universidad?: string;
  carrera?: string;
  materia?: string;
  tipo?: string;
};

export type Usuario = {
  id: string;
  email: string;
  nombre: string;
  universidad: string;
  carrera: string;
};

export type RespuestaLogin = {
  token: string;
  usuario: Usuario;
};

export type DocumentoNuevo = {
  titulo: string;
  materia: string;
  tipo: string;
  universidad?: string;
  carrera?: string;
  palabras_clave?: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// Modos de fallo de la integración frontend -> API (docs/resiliencia/modos-de-fallo.md).
const TIMEOUT_MS = 15000;
const REINTENTOS = 1;
const ESPERA_MS = 1000;

async function pedirConTimeout(url: string, opciones?: RequestInit): Promise<Response> {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), TIMEOUT_MS);
  try {
    return await fetch(url, { ...opciones, signal: control.signal });
  } finally {
    clearTimeout(temporizador);
  }
}

// Reintenta solo ante error de red, timeout o 5xx. Un 4xx no se reintenta.
async function pedirConReintento(url: string, opciones?: RequestInit, intento = 0): Promise<Response> {
  try {
    const res = await pedirConTimeout(url, opciones);
    if (res.status < 500 || intento >= REINTENTOS) return res;
  } catch (error) {
    if (intento >= REINTENTOS) throw error;
  }
  await new Promise((resolver) => setTimeout(resolver, ESPERA_MS));
  return pedirConReintento(url, opciones, intento + 1);
}

// Una sola solicitud con todos los filtros (ADR 0002): cumple el presupuesto de <=3 interacciones.
export async function buscarDocumentos(filtros: Filtros): Promise<ResultadoBusqueda> {
  const params = new URLSearchParams();
  Object.entries(filtros).forEach(([clave, valor]) => {
    if (valor) params.set(clave, valor);
  });
  const res = await pedirConReintento(`${API_URL}/busqueda/documentos?${params.toString()}`);
  if (!res.ok) throw new Error(`Error ${res.status} al buscar documentos`);
  return res.json();
}

export async function loginUsuario(email: string, password: string): Promise<RespuestaLogin> {
  const res = await pedirConTimeout(`${API_URL}/usuarios/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Correo o contraseña incorrectos");
  }
  return res.json();
}

export async function registrarUsuario(datos: {
  email: string;
  password: string;
  nombre: string;
  universidad?: string;
  carrera?: string;
}): Promise<Usuario> {
  const res = await pedirConTimeout(`${API_URL}/usuarios/registro`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Error al crear la cuenta");
  }
  return res.json();
}

export async function obtenerPerfil(token: string): Promise<Usuario> {
  const res = await pedirConTimeout(`${API_URL}/usuarios/perfil`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Sesión inválida o expirada");
  return res.json();
}

export async function cerrarSesion(token: string): Promise<void> {
  await pedirConTimeout(`${API_URL}/usuarios/logout`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  }).catch(() => {});
}

export async function obtenerDocumentosUsuario(token: string): Promise<Documento[]> {
  const res = await pedirConTimeout(`${API_URL}/usuarios/perfil/documentos`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Error al obtener los materiales del usuario");
  const data = await res.json();
  return data.documentos || [];
}

export async function subirDocumentoUsuario(token: string, doc: DocumentoNuevo): Promise<Documento> {
  const res = await pedirConTimeout(`${API_URL}/usuarios/perfil/documentos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(doc),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Error al publicar material");
  }
  return res.json();
}
