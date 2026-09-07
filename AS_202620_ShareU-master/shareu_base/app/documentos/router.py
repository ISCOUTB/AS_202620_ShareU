"""API del módulo documentos.

La persistencia y las operaciones de documentos pertenecen a este módulo.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/documentos", tags=["documentos"])


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "documentos", "estado": "ok"}
