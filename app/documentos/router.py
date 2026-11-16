"""API del módulo documentos.

La persistencia y las operaciones de documentos pertenecen a este módulo.
El corte vertical expone la consulta pública que consume búsqueda y, desde S11,
una publicación idempotente protegida por una credencial administrativa.
Desde el taller de mensajería (S12), publicar emite `documento.publicado` al
outbox para que administración lo ponga en su bandeja de revisión.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.documentos.service import (
    ConflictoIdempotencia,
    ErrorPersistencia,
    obtener_estadisticas_cache,
    registrar_documento,
)
from app.eventos import despachar, publicar
from app.seguridad.autenticacion import exigir_token_admin

router = APIRouter(prefix="/documentos", tags=["documentos"])

TIPO_EVENTO_PUBLICADO = "documento.publicado"


class DocumentoEntrada(BaseModel):
    """Cuerpo aceptado por ``POST /documentos`` (metadatos, no el archivo)."""

    titulo: str = Field(min_length=1, max_length=200)
    universidad: str = Field(min_length=1, max_length=120)
    carrera: str = Field(min_length=1, max_length=120)
    materia: str = Field(min_length=1, max_length=120)
    tipo: str = Field(min_length=1, max_length=60)
    autor: str = Field(min_length=1, max_length=120)
    calificacion: float = Field(ge=0, le=5)
    palabras_clave: str = Field(default="", max_length=400)


def _correlation_id(request: Request) -> str:
    """Reutiliza el `request_id` del middleware para poder seguir la traza."""
    return getattr(request.state, "request_id", None) or str(uuid.uuid4())


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "documentos", "estado": "ok"}


@router.get("/cache")
def cache() -> dict:
    """Estado de la caché de lectura (TTL, hits, misses e invalidaciones)."""
    return obtener_estadisticas_cache()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {"description": "Reintento idempotente: devuelve el documento ya creado."},
        401: {"description": "Credencial administrativa inválida."},
        409: {"description": "La clave de idempotencia se usó con otro contenido."},
        422: {"description": "Cuerpo inválido."},
        503: {"description": "Publicación deshabilitada por falta de configuración."},
    },
)
def publicar_documento(
    payload: DocumentoEntrada,
    request: Request,
    background: BackgroundTasks,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=8),
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    """Publica metadatos de un documento de forma idempotente.

    Repetir la solicitud con la misma ``Idempotency-Key`` y el mismo cuerpo
    devuelve el mismo documento (HTTP 200) sin crear un duplicado y sin emitir
    un segundo evento. Es el diseño de idempotencia de
    `docs/resiliencia/modos-de-fallo.md`.

    El evento `documento.publicado` se entrega **después** de responder
    (`BackgroundTasks`): si el consumidor falla, la publicación no se cae y el
    outbox reintenta (ADR 0015).
    """
    exigir_token_admin(x_admin_token)
    try:
        documento, creado = registrar_documento(
            payload.model_dump(), idempotency_key=idempotency_key
        )
    except ConflictoIdempotencia as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except ErrorPersistencia as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistencia no disponible; reintente más tarde",
        ) from error

    if creado:
        publicar(
            TIPO_EVENTO_PUBLICADO,
            {
                "id_documento": documento["id"],
                "titulo": documento["titulo"],
                "materia": documento["materia"],
                "autor": documento.get("autor"),
            },
            correlation_id=_correlation_id(request),
        )
        background.add_task(despachar)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED if creado else status.HTTP_200_OK,
        content=documento,
    )
