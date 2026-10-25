export type Documento = {
  id: number;
  titulo: string;
  universidad: string;
  carrera: string;
  materia: string;
  tipo: string;
  autor: string;
  calificacion: number;
};

export type ResultadoBusqueda = { total: number; resultados: Documento[] };

export type Filtros = {
  palabra_clave?: string;
  universidad?: string;
  carrera?: string;
  materia?: string;
  tipo?: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// Modos de fallo de la integración frontend -> API (docs/resiliencia/modos-de-fallo.md).
const TIMEOUT_MS = 15000; // Render Free puede tardar en despertar
const REINTENTOS = 1; // un reintento: la búsqueda es un GET idempotente
const ESPERA_MS = 1000;

async function pedirConTimeout(url: string): Promise<Response> {
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), TIMEOUT_MS);
  try {
    return await fetch(url, { signal: control.signal });
  } finally {
    clearTimeout(temporizador);
  }
}

// Reintenta solo ante error de red, timeout o 5xx. Un 4xx no se reintenta.
async function pedirConReintento(url: string): Promise<Response> {
  for (let intento = 0; ; intento++) {
    try {
      const res = await pedirConTimeout(url);
      if (res.status < 500 || intento >= REINTENTOS) return res;
    } catch (error) {
      if (intento >= REINTENTOS) throw error;
    }
    await new Promise((resolver) => setTimeout(resolver, ESPERA_MS));
  }
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
