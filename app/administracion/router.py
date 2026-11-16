"""Módulo: administracion.

Responsabilidad: reportes, moderación y métricas del sistema.
"""
from fastapi import APIRouter, Header, HTTPException, status

from app.administracion.service import (
    estadisticas_eventos,
    listar_revision,
    obtener_estadisticas_cache,
    obtener_metricas,
    resolver_revision,
)
from app.seguridad.autenticacion import exigir_token_admin

router = APIRouter(prefix="/administracion", tags=["administracion"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "administracion", "estado": "ok"}


@router.get("/metricas")
def metricas() -> dict:
    """Métrica consultable ligada al escenario de usabilidad (ficha S8)."""
    return obtener_metricas()


@router.get("/cache")
def cache() -> dict:
    """Estado observable de la caché de lectura (S12 / S14)."""
    return obtener_estadisticas_cache()


@router.get("/eventos")
def eventos() -> dict:
    """Contadores del outbox: pendientes, reintentos, duplicados y fallidos."""
    return estadisticas_eventos()


@router.get(
    "/revision",
    responses={
        401: {"description": "Credencial administrativa inválida."},
        503: {"description": "Lectura deshabilitada por falta de configuración."},
    },
)
def revision(
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> dict:
    """Bandeja de revisión alimentada por el evento `documento.publicado`.

    Contiene nombres de autores y material pendiente de moderación, así que
    exige la misma credencial administrativa que resolver (ADR 0014, S13).
    """
    exigir_token_admin(x_admin_token)
    documentos = listar_revision()
    return {"total": len(documentos), "documentos": documentos}


@router.post(
    "/revision/{id_documento}/resolver",
    responses={
        401: {"description": "Credencial administrativa inválida."},
        404: {"description": "El documento no está en la bandeja de revisión."},
        503: {"description": "Escritura deshabilitada por falta de configuración."},
    },
)
def resolver(
    id_documento: int,
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> dict:
    """Aprueba y retira un documento de la bandeja de revisión."""
    exigir_token_admin(x_admin_token)
    entrada = resolver_revision(id_documento)
    if entrada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El documento no está pendiente de revisión",
        )
    return entrada
