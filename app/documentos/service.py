"""Interfaz pública del módulo documentos."""
from typing import Any

from app.documentos.repository import (
    ConflictoIdempotencia,
    ErrorPersistencia,
    crear_documento,
    estadisticas_cache,
    listar_documentos,
)


def obtener_documentos() -> list[dict[str, Any]]:
    """Devuelve documentos mediante la interfaz pública del módulo."""
    return listar_documentos()


def registrar_documento(
    documento: dict[str, Any], *, idempotency_key: str
) -> tuple[dict[str, Any], bool]:
    """Publica un documento de forma idempotente (ADR 0013 / S11)."""
    return crear_documento(documento, idempotency_key=idempotency_key)


def obtener_estadisticas_cache() -> dict[str, Any]:
    """Estadísticas de la caché de lectura del módulo."""
    return estadisticas_cache()


__all__ = [
    "ConflictoIdempotencia",
    "ErrorPersistencia",
    "obtener_documentos",
    "obtener_estadisticas_cache",
    "registrar_documento",
]
