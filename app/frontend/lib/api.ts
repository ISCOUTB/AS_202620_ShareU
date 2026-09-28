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

// Una sola solicitud con todos los filtros (ADR 0002): cumple el presupuesto de <=3 interacciones.
export async function buscarDocumentos(filtros: Filtros): Promise<ResultadoBusqueda> {
  const params = new URLSearchParams();
  Object.entries(filtros).forEach(([clave, valor]) => {
    if (valor) params.set(clave, valor);
  });
  const res = await fetch(`${API_URL}/busqueda/documentos?${params.toString()}`);
  if (!res.ok) throw new Error(`Error ${res.status} al buscar documentos`);
  return res.json();
}
