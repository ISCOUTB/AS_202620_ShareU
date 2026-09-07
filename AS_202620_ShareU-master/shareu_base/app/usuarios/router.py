"""Módulo: usuarios.

Responsabilidad: registro, autenticación y administración del perfil.
Fontanería únicamente — sin lógica de negocio todavía.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "usuarios", "estado": "ok"}
