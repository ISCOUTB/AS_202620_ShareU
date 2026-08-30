"""Interfaz pública del módulo documentos."""
from typing import Any

from app.documentos.repository import listar_documentos


def obtener_documentos() -> list[dict[str, Any]]:
    """Devuelve documentos mediante la interfaz pública del módulo."""
    return listar_documentos()
