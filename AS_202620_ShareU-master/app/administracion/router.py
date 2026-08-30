"""Módulo: administracion.

Responsabilidad: reportes, moderación y gestión de usuarios/documentos.
Fontanería únicamente — sin lógica de negocio todavía.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/administracion", tags=["administracion"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "administracion", "estado": "ok"}
