"""Bandeja de revisión de documentos publicados (consumidor del evento).

El módulo `administracion` es el dueño de esta bandeja. Se llena al consumir
`documento.publicado`; el consumidor es idempotente por `event_id`, porque el
outbox garantiza entrega **al menos una vez** y un duplicado no puede crear dos
entradas de revisión.
"""
from __future__ import annotations

import threading
from typing import Any

from app.eventos import Evento, ProcesadorIdempotente

_CAMPOS_REQUERIDOS = ("id_documento", "titulo", "materia")

_lock = threading.Lock()
_cola: list[dict[str, Any]] = []
_procesador = ProcesadorIdempotente()


def registrar_para_revision(evento: Evento) -> None:
    """Consumidor del evento `documento.publicado`."""
    payload = evento.payload
    faltantes = [campo for campo in _CAMPOS_REQUERIDOS if campo not in payload]
    if faltantes:
        raise ValueError(f"evento inválido: faltan campos {faltantes}")

    def _agregar(evento_entregado: Evento) -> None:
        with _lock:
            if any(
                entrada["id_documento"] == payload["id_documento"] for entrada in _cola
            ):
                return
            _cola.append(
                {
                    "id_documento": payload["id_documento"],
                    "titulo": payload["titulo"],
                    "materia": payload["materia"],
                    "autor": payload.get("autor"),
                    "event_id": evento_entregado.event_id,
                    "correlation_id": evento_entregado.correlation_id,
                    "recibido_en": evento_entregado.ocurrido_en,
                    "estado": "pendiente",
                }
            )

    _procesador.procesar(evento, _agregar)


def listar_revision() -> list[dict[str, Any]]:
    with _lock:
        return [dict(entrada) for entrada in _cola]


def resolver_revision(id_documento: int) -> dict[str, Any] | None:
    """Retira un documento de la bandeja y devuelve la entrada resuelta."""
    with _lock:
        for indice, entrada in enumerate(_cola):
            if entrada["id_documento"] == id_documento:
                resuelta = dict(_cola.pop(indice))
                resuelta["estado"] = "aprobado"
                return resuelta
    return None


def reinitializar() -> None:
    global _procesador
    with _lock:
        _cola.clear()
    _procesador = ProcesadorIdempotente()
