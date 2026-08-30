"""API del módulo busqueda.

El endpoint concentra los filtros en una sola solicitud, alineado con el
escenario de usabilidad: el estudiante puede buscar y filtrar sin recorrer
varias pantallas.
"""
from fastapi import APIRouter, Query

from app.busqueda.service import buscar_documentos

router = APIRouter(prefix="/busqueda", tags=["busqueda"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "busqueda", "estado": "ok"}


@router.get("/documentos")
def buscar(
    universidad: str | None = Query(default=None),
    carrera: str | None = Query(default=None),
    materia: str | None = Query(default=None),
    tipo: str | None = Query(default=None),
    palabra_clave: str | None = Query(default=None),
    min_calificacion: float | None = Query(default=None, ge=0, le=5),
) -> dict:
    """Busca material académico con filtros opcionales."""
    resultados = buscar_documentos(
        universidad=universidad,
        carrera=carrera,
        materia=materia,
        tipo=tipo,
        palabra_clave=palabra_clave,
        min_calificacion=min_calificacion,
    )
    return {"total": len(resultados), "resultados": resultados}
