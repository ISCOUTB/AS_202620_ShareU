"""Lógica de búsqueda del módulo busqueda."""
from __future__ import annotations

from typing import Any, Callable

from app.documentos.service import obtener_documentos

_Filtro = Callable[[dict[str, Any]], bool]


def _contains(value: str, query: str) -> bool:
    return query.casefold() in value.casefold()


def _coincide_campo(campo: str, valor: str | None) -> _Filtro:
    if valor is None:
        return lambda documento: True
    return lambda documento: _contains(documento[campo], valor)


def _coincide_palabra_clave(palabra_clave: str | None) -> _Filtro:
    if palabra_clave is None:
        return lambda documento: True
    return lambda documento: (
        _contains(documento["titulo"], palabra_clave)
        or _contains(documento["palabras_clave"], palabra_clave)
    )


def _coincide_calificacion(min_calificacion: float | None) -> _Filtro:
    if min_calificacion is None:
        return lambda documento: True
    return lambda documento: documento["calificacion"] >= min_calificacion


def _construir_filtros(
    *,
    universidad: str | None,
    carrera: str | None,
    materia: str | None,
    tipo: str | None,
    palabra_clave: str | None,
    min_calificacion: float | None,
) -> list[_Filtro]:
    """Traduce cada criterio opcional en un predicado independiente."""
    return [
        _coincide_campo("universidad", universidad),
        _coincide_campo("carrera", carrera),
        _coincide_campo("materia", materia),
        _coincide_campo("tipo", tipo),
        _coincide_palabra_clave(palabra_clave),
        _coincide_calificacion(min_calificacion),
    ]


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
    filtros = _construir_filtros(
        universidad=universidad,
        carrera=carrera,
        materia=materia,
        tipo=tipo,
        palabra_clave=palabra_clave,
        min_calificacion=min_calificacion,
    )

    resultados = [
        documento
        for documento in obtener_documentos()
        if all(filtro(documento) for filtro in filtros)
    ]

    resultados.sort(key=lambda documento: (-documento["calificacion"], documento["titulo"]))
    for documento in resultados:
        documento.pop("palabras_clave", None)
    return resultados
