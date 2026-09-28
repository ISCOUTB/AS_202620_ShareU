"""Punto de entrada de ShareU.

Monolito modular: cada dominio (usuarios, documentos, busqueda,
calificaciones, administracion) se monta como un router independiente.
Ningún módulo importa el modelo interno de otro (ver docs/adr/0001).
"""
import json
import logging
import os
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.usuarios.router import router as usuarios_router
from app.documentos.router import router as documentos_router
from app.busqueda.router import router as busqueda_router
from app.calificaciones.router import router as calificaciones_router
from app.administracion.router import router as administracion_router


class _JsonFormatter(logging.Formatter):
    """Formatea cada línea de log como un objeto JSON (log estructurado).

    Campos fijos: timestamp, level, logger, message, y cualquier atributo
    extra pasado vía `logger.info(..., extra={...})` (request_id, path,
    status_code, duration_ms). Esto es lo que pide la ficha S8: campos, no
    cadenas sueltas.
    """

    _EXTRA_FIELDS = ("request_id", "method", "path", "status_code", "duration_ms")

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in self._EXTRA_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False)


def _configurar_logging() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    logger = logging.getLogger("shareu")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


logger = _configurar_logging()

app = FastAPI(title="ShareU")

# Permite probar el frontend (Next.js) contra el backend sin introducir
# dependencias externas. En producción, este origen debe restringirse al
# dominio real de despliegue del frontend (ver docs/adr de despliegue).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("SHAREU_FRONTEND_ORIGIN", "*")],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.middleware("http")
async def registrar_solicitud(request: Request, call_next: Callable):
    """Log estructurado por solicitud: request_id, método, ruta, estado y duración."""
    request_id = str(uuid.uuid4())
    inicio = time.perf_counter()
    response = await call_next(request)
    duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "solicitud atendida",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duracion_ms,
        },
    )
    return response


app.include_router(usuarios_router)
app.include_router(documentos_router)
app.include_router(busqueda_router)
app.include_router(calificaciones_router)
app.include_router(administracion_router)


@app.get("/health")
def health() -> dict:
    return {"estado": "ok"}
