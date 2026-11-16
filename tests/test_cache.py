"""Caché de lectura del repositorio de documentos (ADR 0013, S12/S14)."""
import time

import pytest

from app.documentos import repository

DOCUMENTO = {
    "titulo": "Taller de Caché",
    "universidad": "Universidad Nacional",
    "carrera": "Ingeniería de Sistemas",
    "materia": "Arquitectura de Software",
    "tipo": "Taller",
    "autor": "Dayana",
    "calificacion": 4.9,
    "palabras_clave": "cache ttl invalidacion",
}


def test_segunda_lectura_no_va_a_firestore(firestore_falso):
    repository.listar_documentos()
    lecturas = firestore_falso.lecturas

    repository.listar_documentos()

    assert firestore_falso.lecturas == lecturas
    assert repository.estadisticas_cache()["hits"] >= 1


def test_el_ttl_expira_la_entrada(firestore_falso):
    repository._cache.configurar_ttl(0.01)
    repository.listar_documentos(usar_cache=False)
    repository.listar_documentos()  # llena la caché
    lecturas = firestore_falso.lecturas
    time.sleep(0.05)

    repository.listar_documentos()

    assert firestore_falso.lecturas > lecturas
    assert repository.estadisticas_cache()["misses"] >= 1


def test_una_escritura_invalida_la_cache(firestore_falso):
    repository.listar_documentos()  # caché con los 5 documentos iniciales

    creado, es_nuevo = repository.crear_documento(
        DOCUMENTO, idempotency_key="cache-invalida-0001"
    )

    assert es_nuevo is True
    documentos = repository.listar_documentos()
    assert any(documento["id"] == creado["id"] for documento in documentos)
    assert repository.estadisticas_cache()["invalidaciones"] >= 1


def test_la_cache_no_se_muta_desde_fuera(firestore_falso):
    repository.listar_documentos()
    documentos = repository.listar_documentos()
    documentos[0]["titulo"] = "mutado por el consumidor"

    assert repository.listar_documentos()[0]["titulo"] == "Taller de Python"


def test_estadisticas_expuestas(firestore_falso):
    repository.listar_documentos()
    estadisticas = repository.estadisticas_cache()

    assert estadisticas["ttl_segundos"] == repository._cache.ttl
    assert estadisticas["entradas"] == 5
    assert {"hits", "misses", "invalidaciones"} <= set(estadisticas)


def test_configurar_ttl_negativo_equivale_a_cero(firestore_falso):
    repository._cache.configurar_ttl(-5)

    assert repository._cache.ttl == 0.0


@pytest.mark.parametrize("clave", ["", "corta"])
def test_clave_de_idempotencia_demasiado_corta(firestore_falso, clave):
    with pytest.raises(ValueError):
        repository.crear_documento(DOCUMENTO, idempotency_key=clave)
