"""Modo de fallo «responde dos veces» de la integración frontend -> API (S11).

Ver docs/resiliencia/modos-de-fallo.md. La búsqueda es un GET de solo lectura:
repetirla no debe cambiar los datos ni el resultado. El único efecto aceptado de
la repetición es que la métrica (en memoria) la cuenta dos veces (ADR 0008).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PARAMS = {"materia": "Programación"}


def test_busqueda_repetida_devuelve_lo_mismo():
    primera = client.get("/busqueda/documentos", params=PARAMS).json()
    segunda = client.get("/busqueda/documentos", params=PARAMS).json()

    assert primera == segunda


def test_repetir_busquedas_no_modifica_los_datos():
    antes = client.get("/busqueda/documentos").json()
    for _ in range(3):
        client.get("/busqueda/documentos", params=PARAMS)
    despues = client.get("/busqueda/documentos").json()

    assert antes == despues


def test_busqueda_repetida_se_cuenta_dos_veces_en_la_metrica():
    antes = client.get("/administracion/metricas").json()["total_busquedas"]
    client.get("/busqueda/documentos", params=PARAMS)
    client.get("/busqueda/documentos", params=PARAMS)
    despues = client.get("/administracion/metricas").json()["total_busquedas"]

    assert despues == antes + 2
