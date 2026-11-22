"""API del módulo busqueda.

El endpoint concentra los filtros en una sola solicitud, alineado con el
escenario de usabilidad: el estudiante puede buscar y filtrar sin recorrer
varias pantallas.
"""
from fastapi import APIRouter, HTTPException, Query, status

from app.busqueda.service import buscar_documentos
from app.documentos.service import ErrorPersistencia

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
    try:
        resultados = buscar_documentos(
            universidad=universidad,
            carrera=carrera,
            materia=materia,
            tipo=tipo,
            palabra_clave=palabra_clave,
            min_calificacion=min_calificacion,
        )
    except ErrorPersistencia as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistencia no disponible; reintente más tarde",
        ) from error
    return {"total": len(resultados), "resultados": resultados}
