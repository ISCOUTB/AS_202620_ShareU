"""Prueba que el esqueleto arranca y cada módulo responde."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"estado": "ok"}


def test_modulos_responden():
    modulos = ["usuarios", "documentos", "busqueda", "calificaciones", "administracion"]
    for modulo in modulos:
        response = client.get(f"/{modulo}/ping")
        assert response.status_code == 200
        assert response.json()["modulo"] == modulo
