"""Prueba el corte vertical: busqueda -> documentos -> repository."""
import os

from fastapi.testclient import TestClient

os.environ["APP_DB_PATH"] = "/tmp/test_app.db"

from app.main import app  # noqa: E402

client = TestClient(app)


def test_busqueda_sin_filtros_devuelve_lista():
    response = client.get("/busqueda/documentos")
    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "resultados" in body
