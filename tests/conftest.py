"""Firestore falso en memoria: las pruebas no necesitan credenciales ni red (ADR 0012)."""
import threading

import pytest

from app import eventos
from app.administracion import revision
from app.documentos import repository
from firestore_falso import Cliente


@pytest.fixture(autouse=True)
def firestore_falso(monkeypatch):
    cliente = Cliente()
    monkeypatch.setattr(repository, "_cliente", lambda: cliente)
    monkeypatch.setattr(repository, "_inicializado", False)
    monkeypatch.setattr(repository, "_cache", repository._CacheDocumentos())
    monkeypatch.setattr(repository, "_lock_inicializacion", threading.Lock())
    return cliente


@pytest.fixture(autouse=True)
def estado_de_mensajeria_limpio():
    """Cada prueba arranca con el outbox y la bandeja de revisión vacíos."""
    eventos.reinitializar()
    revision.reinitializar()
    yield
    eventos.reinitializar()
    revision.reinitializar()
