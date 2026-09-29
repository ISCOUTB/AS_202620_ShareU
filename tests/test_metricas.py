"""Pruebas de la métrica ligada al escenario de usabilidad (ADR 0008).

Usan diferencias (antes/después) porque el contador vive en memoria y lo
comparten todas las pruebas del proceso.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _metricas() -> dict:
    return client.get("/administracion/metricas").json()


def test_busqueda_con_resultados_no_cuenta_como_sin_resultados():
    antes = _metricas()
    client.get("/busqueda/documentos", params={"materia": "Programación"})
    despues = _metricas()

    assert despues["total_busquedas"] == antes["total_busquedas"] + 1
    assert despues["busquedas_sin_resultados"] == antes["busquedas_sin_resultados"]


def test_busqueda_sin_resultados_se_cuenta():
    antes = _metricas()
    client.get("/busqueda/documentos", params={"materia": "Materia Inexistente"})
    despues = _metricas()

    assert despues["total_busquedas"] == antes["total_busquedas"] + 1
    assert despues["busquedas_sin_resultados"] == antes["busquedas_sin_resultados"] + 1


def test_tasa_es_sin_resultados_sobre_total():
    client.get("/busqueda/documentos", params={"materia": "Materia Inexistente"})
    m = _metricas()

    esperado = round(m["busquedas_sin_resultados"] / m["total_busquedas"], 4)
    assert m["tasa_busquedas_sin_resultados"] == esperado
