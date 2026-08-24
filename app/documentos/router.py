"""Módulo: documentos.

Responsabilidad: subida, clasificación (universidad/carrera/materia) y
descarga de material académico. Fontanería únicamente — sin lógica de
negocio todavía (ver docs/adr/0001).
"""
from fastapi import APIRouter

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "documentos", "estado": "ok"}
