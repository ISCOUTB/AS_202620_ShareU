"""Outbox en proceso: publicación, reintentos, deduplicación y cola de fallidos.

Taller aplicado «Mensajes y consistencia» (semana 12). La operación real del
proyecto es **publicar un documento**: después de persistirlo, el sistema debe
avisar al módulo de administración para que el documento entre a la bandeja de
revisión. Ese aviso no puede hacer fallar la publicación ni bloquear al
estudiante, así que se emite como evento y se procesa aparte.

Propiedades implementadas (una por punto del taller):

1. Contrato: `docs/eventos/contrato-evento.md` + esquema JSON versionado.
2. Garantía de entrega: **al menos una vez**; el consumidor debe ser idempotente.
3. Duplicados: `ProcesadorIdempotente` descarta por `event_id`.
4. Reintentos con espera creciente (1 s y 2 s…) y cola de fallidos.
5. Pruebas: `tests/test_eventos.py` (duplicado y fallo recuperable).
6. Trazabilidad: cada línea de log lleva `event_id` y `correlation_id`.
7. Decisión: ADR 0015 frente a la alternativa síncrona.

Límites declarados en `docs/eventos/limites.md`: el outbox vive en memoria del
proceso; un reinicio descarta los eventos pendientes. No sustituye a un broker
real y por eso no se presenta como mensajería de producción.
"""
from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger("shareu.eventos")

VERSION_ACTUAL = 1
MAX_INTENTOS = 3
ESPERA_BASE_SEGUNDOS = float(os.getenv("SHAREU_EVENTO_ESPERA_BASE_SEGUNDOS", "1.0"))

Manejador = Callable[["Evento"], None]


@dataclass
class Evento:
    """Mensaje del outbox. La forma pública está congelada por el contrato."""

    tipo: str
    payload: dict[str, Any]
    correlation_id: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = VERSION_ACTUAL
    ocurrido_en: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    intentos: int = 0
    estado: str = "pendiente"  # pendiente | procesado | fallido
    ultimo_error: str | None = None
    proximo_intento_en: float = 0.0

    def como_dict(self) -> dict[str, Any]:
        """Representación que viaja en el mensaje (sin estado interno de envío)."""
        return {
            "event_id": self.event_id,
            "tipo": self.tipo,
            "version": self.version,
            "ocurrido_en": self.ocurrido_en,
            "correlation_id": self.correlation_id,
            "payload": dict(self.payload),
        }


_lock = threading.Lock()
_pendientes: list[Evento] = []
_procesados: dict[str, Evento] = {}
_fallidos: list[Evento] = []
_suscriptores: dict[str, list[tuple[str, Manejador]]] = {}
_contadores: dict[str, int] = {
    "publicados": 0,
    "procesados": 0,
    "duplicados": 0,
    "reintentos": 0,
    "fallidos": 0,
}


def _contar(campo: str) -> None:
    with _lock:
        _contadores[campo] = _contadores.get(campo, 0) + 1


def suscribir(tipo: str, manejador: Manejador, *, nombre: str | None = None) -> None:
    """Registra un consumidor para un tipo de evento (idempotente por nombre)."""
    nombre = nombre or getattr(manejador, "__qualname__", repr(manejador))
    with _lock:
        actuales = _suscriptores.setdefault(tipo, [])
        if any(existente == nombre for existente, _ in actuales):
            return
        actuales.append((nombre, manejador))


def publicar(
    tipo: str,
    payload: dict[str, Any],
    *,
    correlation_id: str,
) -> Evento:
    """Añade el evento al outbox. No entrega: eso lo hace `despachar`."""
    evento = Evento(tipo=tipo, payload=dict(payload), correlation_id=correlation_id)
    with _lock:
        _pendientes.append(evento)
    _contar("publicados")
    logger.info(
        "evento publicado",
        extra={
            "event_id": evento.event_id,
            "correlation_id": evento.correlation_id,
            "tipo_evento": evento.tipo,
            "intento": 0,
            "estado_evento": evento.estado,
        },
    )
    return evento


def despachar(*, ahora: float | None = None, forzar: bool = False) -> int:
    """Entrega los eventos pendientes cuya espera ya venció.

    Devuelve cuántos eventos quedaron procesados en esta pasada. Un fallo del
    consumidor no se propaga: el evento queda pendiente con espera creciente o
    pasa a la cola de fallidos cuando agota `MAX_INTENTOS`.
    """
    ahora = time.monotonic() if ahora is None else ahora
    with _lock:
        candidatos = [
            evento
            for evento in _pendientes
            if forzar or evento.proximo_intento_en <= ahora
        ]
    entregados = 0
    for evento in candidatos:
        if _entregar(evento, ahora):
            entregados += 1
    return entregados


def _entregar(evento: Evento, ahora: float) -> bool:
    with _lock:
        suscriptores = list(_suscriptores.get(evento.tipo, []))
    if not suscriptores:
        # Sin consumidores no es un fallo: el evento queda para cuando exista uno.
        return False
    try:
        for _, manejador in suscriptores:
            manejador(evento)
    except Exception as error:  # el fallo del consumidor no rompe al productor
        evento.intentos += 1
        evento.ultimo_error = f"{type(error).__name__}: {error}"
        if evento.intentos >= MAX_INTENTOS:
            with _lock:
                if evento in _pendientes:
                    _pendientes.remove(evento)
                _fallidos.append(evento)
            evento.estado = "fallido"
            _contar("fallidos")
            logger.error(
                "evento enviado a la cola de fallidos",
                extra={
                    "event_id": evento.event_id,
                    "correlation_id": evento.correlation_id,
                    "tipo_evento": evento.tipo,
                    "intento": evento.intentos,
                    "estado_evento": evento.estado,
                },
            )
        else:
            espera = ESPERA_BASE_SEGUNDOS * (2 ** (evento.intentos - 1))
            evento.proximo_intento_en = ahora + espera
            _contar("reintentos")
            logger.warning(
                "evento reprogramado",
                extra={
                    "event_id": evento.event_id,
                    "correlation_id": evento.correlation_id,
                    "tipo_evento": evento.tipo,
                    "intento": evento.intentos,
                    "estado_evento": evento.estado,
                    "espera_segundos": espera,
                },
            )
        return False
    with _lock:
        if evento in _pendientes:
            _pendientes.remove(evento)
        evento.estado = "procesado"
        _procesados[evento.event_id] = evento
    _contar("procesados")
    logger.info(
        "evento procesado",
        extra={
            "event_id": evento.event_id,
            "correlation_id": evento.correlation_id,
            "tipo_evento": evento.tipo,
            "intento": evento.intentos,
            "estado_evento": evento.estado,
        },
    )
    return True


def reenviar(event_id: str) -> Evento | None:
    """Reencola un evento ya entregado (simula una reentrega «al menos una vez»).

    Se usa en pruebas y en la demostración del taller. El consumidor debe
    descartarlo por `event_id`; si lo procesa otra vez, la deduplicación falla.
    """
    with _lock:
        original = _procesados.get(event_id)
    if original is None:
        return None
    copia = Evento(
        tipo=original.tipo,
        payload=dict(original.payload),
        correlation_id=original.correlation_id,
        event_id=original.event_id,
    )
    with _lock:
        _pendientes.append(copia)
    logger.warning(
        "evento reenviado",
        extra={
            "event_id": copia.event_id,
            "correlation_id": copia.correlation_id,
            "tipo_evento": copia.tipo,
            "intento": 0,
            "estado_evento": "pendiente",
        },
    )
    return copia


def estadisticas() -> dict[str, Any]:
    """Contadores observables del outbox (se exponen en la API)."""
    with _lock:
        return {
            "garantia": "al menos una vez",
            "max_intentos": MAX_INTENTOS,
            "espera_base_segundos": ESPERA_BASE_SEGUNDOS,
            "pendientes": len(_pendientes),
            "fallidos": len(_fallidos),
            **_contadores,
        }


def pendientes() -> list[dict[str, Any]]:
    """Copia de los eventos pendientes, para diagnóstico y pruebas."""
    with _lock:
        return [evento.como_dict() for evento in _pendientes]


def fallidos() -> list[dict[str, Any]]:
    """Cola de mensajes fallidos (DLQ)."""
    with _lock:
        return [
            {**evento.como_dict(), "intentos": evento.intentos, "error": evento.ultimo_error}
            for evento in _fallidos
        ]


def reinitializar() -> None:
    """Vacía estado y contadores. Conserva las suscripciones (configuración)."""
    with _lock:
        _pendientes.clear()
        _procesados.clear()
        _fallidos.clear()
        for campo in _contadores:
            _contadores[campo] = 0


class ProcesadorIdempotente:
    """Descarta eventos ya vistos por su `event_id`.

    Con garantía «al menos una vez» el mismo mensaje puede llegar dos veces.
    Este guardián es lo que evita que un duplicado produzca dos efectos.
    """

    def __init__(self) -> None:
        self._vistos: set[str] = set()
        self._lock = threading.Lock()

    def procesar(self, evento: Evento, accion: Callable[[Evento], None]) -> bool:
        """Ejecuta `accion` solo la primera vez. Devuelve si hubo efecto."""
        with self._lock:
            if evento.event_id in self._vistos:
                duplicado = True
            else:
                duplicado = False
        if duplicado:
            _contar("duplicados")
            logger.warning(
                "evento duplicado descartado",
                extra={
                    "event_id": evento.event_id,
                    "correlation_id": evento.correlation_id,
                    "tipo_evento": evento.tipo,
                    "intento": evento.intentos,
                    "estado_evento": "duplicado",
                },
            )
            return False
        accion(evento)
        with self._lock:
            self._vistos.add(evento.event_id)
        return True
