"""Lógica de búsqueda del módulo busqueda."""
from __future__ import annotations

from typing import Any

from app.documentos.service import obtener_documentos


def _contains(value: str, query: str) -> bool:
    return query.casefold() in value.casefold()


def buscar_documentos(
    *,
    universidad: str | None = None,
    carrera: str | None = None,
    materia: str | None = None,
    tipo: str | None = None,
    palabra_clave: str | None = None,
    min_calificacion: float | None = None,
) -> list[dict[str, Any]]:
    """Filtra y ordena documentos usando los criterios disponibles.

    Todos los filtros son opcionales. Los resultados se ordenan por
    calificación descendente para priorizar material mejor valorado.
    """
    documentos = obtener_documentos()
    resultados = []

    for documento in documentos:
        if universidad and not _contains(documento["universidad"], universidad):
            continue
        if carrera and not _contains(documento["carrera"], carrera):
            continue
        if materia and not _contains(documento["materia"], materia):
            continue
        if tipo and not _contains(documento["tipo"], tipo):
            continue
        if palabra_clave and not (
            _contains(documento["titulo"], palabra_clave)
            or _contains(documento["palabras_clave"], palabra_clave)
        ):
            continue
        if min_calificacion is not None and documento["calificacion"] < min_calificacion:
            continue
        resultados.append(documento)

    resultados.sort(key=lambda documento: (-documento["calificacion"], documento["titulo"]))
    for documento in resultados:
        documento.pop("palabras_clave", None)
    return resultados
