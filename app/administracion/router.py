"""Módulo: administracion.

Responsabilidad: reportes, moderación y métricas del sistema.
"""
from fastapi import APIRouter

from app.administracion.metricas import obtener_metricas

router = APIRouter(prefix="/administracion", tags=["administracion"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "administracion", "estado": "ok"}


@router.get("/metricas")
def metricas() -> dict:
    """Métrica consultable ligada al escenario de usabilidad (ficha S8)."""
    return obtener_metricas()
