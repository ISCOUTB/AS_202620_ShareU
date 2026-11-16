"""Interfaz pública del módulo administracion.

Otros módulos (p. ej. búsqueda) registran y consultan métricas solo a través
de este archivo, nunca importando `metricas.py` directamente (ADR 0008).
"""
from app.administracion.metricas import obtener_metricas, registrar_busqueda
from app.administracion.revision import (
    listar_revision,
    registrar_para_revision,
    reinitializar as reinitializar_revision,
    resolver_revision,
)
from app.documentos.service import obtener_estadisticas_cache
from app.eventos import estadisticas as estadisticas_eventos

__all__ = [
    "estadisticas_eventos",
    "listar_revision",
    "obtener_estadisticas_cache",
    "obtener_metricas",
    "registrar_busqueda",
    "registrar_para_revision",
    "reinitializar_revision",
    "resolver_revision",
]
