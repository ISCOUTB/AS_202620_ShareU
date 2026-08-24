"""Módulo: busqueda.

Responsabilidad: filtrado y ranking de resultados. Es el módulo crítico
para el escenario de usabilidad priorizado (docs/aspectos.md).
Fontanería únicamente — sin lógica de negocio todavía.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/busqueda", tags=["busqueda"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "busqueda", "estado": "ok"}
