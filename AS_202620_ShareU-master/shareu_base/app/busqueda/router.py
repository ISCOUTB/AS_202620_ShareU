"""API del módulo busqueda.

El endpoint concentra los filtros en una sola solicitud.
"""
from fastapi import APIRouter

from app.busqueda.service import buscar_documentos

router = APIRouter(prefix="/busqueda", tags=["busqueda"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "busqueda", "estado": "ok"}


@router.get("/documentos")
def buscar(palabra_clave: str | None = None) -> dict:
    """Busca material con filtros opcionales."""
    resultados = buscar_documentos(palabra_clave=palabra_clave)
    return {"total": len(resultados), "resultados": resultados}
