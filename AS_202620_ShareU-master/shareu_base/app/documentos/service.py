"""Interfaz pública del módulo documentos.

Otros módulos deben consumir estas funciones en vez de acceder
directamente al repositorio o a la base de datos.
"""
from typing import Any

from app.documentos.repository import listar_documentos


def obtener_documentos() -> list[dict[str, Any]]:
    """Devuelve documentos mediante la interfaz pública del módulo."""
    return listar_documentos()
