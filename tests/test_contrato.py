"""Prueba de contrato: las respuestas reales cumplen ``docs/api/openapi.yaml``.

No usa un servidor externo: levanta la app con ``TestClient`` y el Firestore
falso de ``conftest.py``. La prueba incluye un caso de mutación incompatible
para demostrar que el contrato se verifica de verdad (ficha S7 / deriva D2 de
S10): si el esquema cambia de forma incompatible, la validación falla.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import app

RAIZ = Path(__file__).resolve().parents[1]
CONTRATO = yaml.safe_load((RAIZ / "docs" / "api" / "openapi.yaml").read_text(encoding="utf-8"))
client = TestClient(app)


def _resolver(nodo: Any) -> Any:
    """Resuelve ``$ref`` locales del documento OpenAPI."""
    if isinstance(nodo, dict):
        if "$ref" in nodo:
            referencia = nodo["$ref"]
            assert referencia.startswith("#/"), referencia
            actual: Any = CONTRATO
            for parte in referencia[2:].split("/"):
                actual = actual[parte]
            return _resolver(actual)
        return {clave: _resolver(valor) for clave, valor in nodo.items()}
    if isinstance(nodo, list):
        return [_resolver(elemento) for elemento in nodo]
    return nodo


def _esquema(nombre: str) -> dict[str, Any]:
    return _resolver(CONTRATO["components"]["schemas"][nombre])


def _validar(nombre: str, payload: Any) -> None:
    jsonschema.validate(instance=payload, schema=_esquema(nombre))


def test_health_cumple_el_contrato():
    respuesta = client.get("/health")

    assert respuesta.status_code == 200
    _validar("Estado", respuesta.json())


def test_los_cinco_pings_cumplen_el_contrato():
    for modulo in ("usuarios", "documentos", "busqueda", "calificaciones", "administracion"):
        respuesta = client.get(f"/{modulo}/ping")
        assert respuesta.status_code == 200
        _validar("EstadoModulo", respuesta.json())


def test_metricas_cumplen_el_contrato():
    respuesta = client.get("/administracion/metricas")

    assert respuesta.status_code == 200
    _validar("Metricas", respuesta.json())


def test_cache_cumple_el_contrato():
    respuesta = client.get("/administracion/cache")

    assert respuesta.status_code == 200
    _validar("EstadisticasCache", respuesta.json())


def test_eventos_cumplen_el_contrato():
    respuesta = client.get("/administracion/eventos")

    assert respuesta.status_code == 200
    _validar("EstadisticasEventos", respuesta.json())


def test_bandeja_de_revision_cumple_el_contrato(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", "token-contrato-123")
    respuesta = client.get(
        "/administracion/revision",
        headers={"X-Admin-Token": "token-contrato-123"},
    )

    assert respuesta.status_code == 200
    _validar("BandejaRevision", respuesta.json())



def test_busqueda_con_resultados_cumple_el_contrato():
    respuesta = client.get("/busqueda/documentos", params={"materia": "Programación"})

    assert respuesta.status_code == 200
    _validar("ResultadoBusqueda", respuesta.json())


def test_busqueda_sin_resultados_cumple_el_contrato():
    respuesta = client.get("/busqueda/documentos", params={"materia": "No existe"})

    assert respuesta.status_code == 200
    _validar("ResultadoBusqueda", respuesta.json())


def test_error_de_validacion_cumple_el_contrato():
    respuesta = client.get("/busqueda/documentos", params={"min_calificacion": 9})

    assert respuesta.status_code == 422
    _validar("ErrorValidacion", respuesta.json())


def test_publicacion_cumple_el_contrato(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", "token-contrato-123")
    respuesta = client.post(
        "/documentos",
        headers={
            "Idempotency-Key": "contrato-publicacion-0001",
            "X-Admin-Token": "token-contrato-123",
        },
        json={
            "titulo": "Guía de Contrato",
            "universidad": "Universidad Nacional",
            "carrera": "Ingeniería de Sistemas",
            "materia": "Arquitectura de Software",
            "tipo": "Guía",
            "autor": "Steven",
            "calificacion": 4.1,
        },
    )

    assert respuesta.status_code == 201
    _validar("DocumentoResumen", respuesta.json())


def test_el_contrato_detecta_un_cambio_incompatible():
    """Mutación: si el esquema renombra ``resultados``, la respuesta deja de cumplir."""
    real = client.get("/busqueda/documentos").json()
    esquema_mutado = copy.deepcopy(_esquema("ResultadoBusqueda"))
    propiedades = esquema_mutado["properties"]
    propiedades["items"] = propiedades.pop("resultados")
    esquema_mutado["required"] = ["total", "items"]

    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=real, schema=esquema_mutado)


def test_el_contrato_declara_las_rutas_implementadas():
    rutas = set(CONTRATO["paths"])
    implementadas = {
        "/health",
        "/usuarios/ping",
        "/documentos/ping",
        "/documentos",
        "/documentos/cache",
        "/busqueda/ping",
        "/busqueda/documentos",
        "/calificaciones/ping",
        "/administracion/ping",
        "/administracion/metricas",
        "/administracion/cache",
        "/administracion/eventos",
        "/administracion/revision",
        "/administracion/revision/{id_documento}/resolver",
    }

    assert implementadas <= rutas


def test_el_contrato_es_json_serializable_y_versionado():
    assert CONTRATO["openapi"].startswith("3.1.")
    assert CONTRATO["info"]["version"]
    json.dumps(CONTRATO)  # no debe contener tipos no serializables
