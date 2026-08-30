"""Pruebas del corte vertical de búsqueda."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_busqueda_sin_filtros_devuelve_documentos():
    response = client.get("/busqueda/documentos")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert all("titulo" in documento for documento in body["resultados"])


def test_busqueda_filtra_por_materia():
    response = client.get("/busqueda/documentos", params={"materia": "Programación"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["resultados"][0]["titulo"] == "Taller de Python"


def test_busqueda_filtra_por_palabra_clave():
    response = client.get("/busqueda/documentos", params={"palabra_clave": "SQL"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["resultados"][0]["materia"] == "Bases de Datos"


def test_busqueda_combina_filtros():
    response = client.get(
        "/busqueda/documentos",
        params={
            "universidad": "Universidad Nacional",
            "carrera": "Ingeniería de Sistemas",
            "materia": "Arquitectura",
            "min_calificacion": 4.5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["resultados"][0]["autor"] == "María"


def test_busqueda_sin_resultados():
    response = client.get(
        "/busqueda/documentos",
        params={"materia": "Materia Inexistente"},
    )

    assert response.status_code == 200
    assert response.json() == {"total": 0, "resultados": []}
