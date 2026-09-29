"""Medición del escenario de usabilidad (docs/aspectos/aspectos.md).

Interacciones = campos que el estudiante llena + 1 clic en «Buscar».
Umbral: <= 3. Para cada documento del catálogo se busca la combinación más
corta de filtros que lo devuelve como único resultado.

Es un indicador técnico sobre los datos de ejemplo, no una prueba con
usuarios reales (ver docs/evidencia/medicion-usabilidad.md).
"""
from itertools import combinations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
FACETAS = ["materia", "tipo", "carrera", "universidad"]
UMBRAL = 3


def _interacciones_minimas(documento: dict) -> int:
    for k in range(1, len(FACETAS) + 1):
        for campos in combinations(FACETAS, k):
            params = {campo: documento[campo] for campo in campos}
            if client.get("/busqueda/documentos", params=params).json()["total"] == 1:
                return k + 1
    return len(FACETAS) + 2  # ni con todas las facetas es único


def test_todo_documento_se_encuentra_en_3_interacciones_o_menos():
    catalogo = client.get("/busqueda/documentos").json()["resultados"]
    peor = max(_interacciones_minimas(d) for d in catalogo)
    assert peor <= UMBRAL
