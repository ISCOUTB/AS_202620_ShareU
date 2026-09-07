"""Módulo: calificaciones.

Responsabilidad: valoración de documentos por parte de los usuarios.
Fontanería únicamente — sin lógica de negocio todavía.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/calificaciones", tags=["calificaciones"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "calificaciones", "estado": "ok"}
