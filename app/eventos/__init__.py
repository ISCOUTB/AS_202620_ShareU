"""Infraestructura de mensajería en proceso (outbox) del proyecto.

Ver `app/eventos/outbox.py` y `docs/eventos/contrato-evento.md`.
"""
from app.eventos.outbox import (
    MAX_INTENTOS,
    Evento,
    ProcesadorIdempotente,
    despachar,
    estadisticas,
    fallidos,
    pendientes,
    publicar,
    reenviar,
    reinitializar,
    suscribir,
)

__all__ = [
    "MAX_INTENTOS",
    "Evento",
    "ProcesadorIdempotente",
    "despachar",
    "estadisticas",
    "fallidos",
    "pendientes",
    "publicar",
    "reenviar",
    "reinitializar",
    "suscribir",
]
