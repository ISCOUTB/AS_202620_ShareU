"""Lógica de búsqueda del módulo busqueda."""
from __future__ import annotations

from typing import Any

from app.documentos.service import obtener_documentos


def _contains(value: str, query: str) -> bool:
    return query.casefold() in value.casefold()


def buscar_documentos(*, palabra_clave: str | None = None) -> list[dict[str, Any]]:
    """Filtra documentos por palabra clave. Todos los filtros son opcionales."""
    documentos = obtener_documentos()
    if not palabra_clave:
        return documentos
    return [d for d in documentos if _contains(d["titulo"], palabra_clave)]
