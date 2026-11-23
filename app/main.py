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
from fastapi.responses import JSONResponse

from app.usuarios.router import router as usuarios_router
from app.documentos.router import router as documentos_router
from app.busqueda.router import router as busqueda_router
from app.calificaciones.router import router as calificaciones_router
from app.administracion.router import router as administracion_router

from app import eventos
from app.administracion.service import registrar_para_revision


class _JsonFormatter(logging.Formatter):
    """Formatea cada línea de log como un objeto JSON (log estructurado).

    Campos fijos: timestamp, level, logger, message, y cualquier atributo
    extra pasado vía `logger.info(..., extra={...})` (request_id, path,
    status_code, duration_ms). Esto es lo que pide la ficha S8: campos, no
    cadenas sueltas.
    """

    _EXTRA_FIELDS = (
        "request_id",
        "method",
        "path",
        "status_code",
        "duration_ms",
        # Trazabilidad de mensajes (taller S12): permiten seguir un evento
        # desde el productor (documentos) hasta el consumidor (administración).
        "event_id",
        "correlation_id",
        "tipo_evento",
        "intento",
        "estado_evento",
        "espera_segundos",
    )

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
        # FIX: incluir traceback completo cuando existe (logger.exception lo provee)
        # Esto no expone secretos: solo muestra tipos de excepción y líneas de código.
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
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

# Punto de composición: el módulo dueño de la bandeja de revisión se suscribe
# al evento que publica documentos. Ningún módulo importa a otro; el cableado
# vive aquí (ADR 0015). La suscripción es idempotente por nombre.
eventos.suscribir(
    "documento.publicado",
    registrar_para_revision,
    nombre="administracion.revision",
)


def _origenes_permitidos() -> list[str]:
    """Orígenes CORS explícitos; nunca ``*`` por omisión (ADR 0014).

    En producción `SHAREU_FRONTEND_ORIGIN` contiene el dominio institucional
    (por ejemplo ``https://shareu.iscoutb.dev``). En local se aceptan los dos
    orígenes de Next.js. Varios orígenes se separan con coma.
    """
    configurado = os.getenv("SHAREU_FRONTEND_ORIGIN", "")
    if configurado.strip():
        return [origen.strip() for origen in configurado.split(",") if origen.strip()]
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_origenes_permitidos(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Idempotency-Key", "X-Admin-Token", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

_RUTAS_DOCUMENTACION = ("/docs", "/redoc", "/openapi.json")


def _es_documentacion(path: str) -> bool:
    return path == "/openapi.json" or path.startswith("/docs") or path.startswith("/redoc")


@app.middleware("http")
async def cabeceras_seguridad(request: Request, call_next: Callable):
    """Cabeceras de endurecimiento HTTP (ADR 0014, amenazas S13).

    La API no sirve HTML propio, así que la CSP puede ser restrictiva. Las
    rutas de Swagger/ReDoc necesitan scripts y estilos de su CDN, por eso se
    excluyen de la CSP estricta (siguen recibiendo el resto de cabeceras).
    """
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
    )
    response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
    if _es_documentacion(request.url.path):
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "frame-ancestors 'none'",
        )
    else:
        response.headers.setdefault(
            "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"
        )
    esquema = request.headers.get("x-forwarded-proto", request.url.scheme)
    if esquema == "https":
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
        )
    return response


@app.middleware("http")
async def registrar_solicitud(request: Request, call_next: Callable):
    """Log estructurado por solicitud: request_id, método, ruta, estado y duración."""
    request_id = str(uuid.uuid4())
    # El handler y los eventos que emite reutilizan este id como correlación.
    request.state.request_id = request_id
    inicio = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duracion_ms = round((time.perf_counter() - inicio) * 1000, 2)
        logger.exception(
            "solicitud fallida",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duracion_ms,
            },
        )
        respuesta = JSONResponse(
            status_code=500, content={"detail": "Error interno del servidor"}
        )
        respuesta.headers["X-Request-ID"] = request_id
        return respuesta
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
