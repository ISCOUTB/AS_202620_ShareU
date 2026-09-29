"""Interfaz pública del módulo administracion.

Otros módulos (p. ej. búsqueda) registran y consultan métricas solo a través
de este archivo, nunca importando `metricas.py` directamente (ADR 0008).
"""
from app.administracion.metricas import obtener_metricas, registrar_busqueda

__all__ = ["obtener_metricas", "registrar_busqueda"]
