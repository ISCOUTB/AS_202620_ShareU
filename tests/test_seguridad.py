"""Cabeceras de seguridad y CORS restringido (ADR 0014, S13)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_cabeceras_de_endurecimiento():
    respuesta = client.get("/health")

    assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
    assert respuesta.headers["X-Frame-Options"] == "DENY"
    assert respuesta.headers["Referrer-Policy"] == "no-referrer"
    assert "Content-Security-Policy" in respuesta.headers
    assert "geolocation=()" in respuesta.headers["Permissions-Policy"]


def test_hsts_solo_detras_de_https():
    sin_https = client.get("/health")
    con_https = client.get("/health", headers={"X-Forwarded-Proto": "https"})

    assert "Strict-Transport-Security" not in sin_https.headers
    assert "max-age=31536000" in con_https.headers["Strict-Transport-Security"]


def test_cors_permite_el_origen_local_de_nextjs():
    respuesta = client.get("/health", headers={"Origin": "http://localhost:3000"})

    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_rechaza_un_origen_desconocido():
    respuesta = client.get("/health", headers={"Origin": "https://atacante.example"})

    assert "access-control-allow-origin" not in respuesta.headers


def test_la_documentacion_conserva_su_csp_amplia():
    respuesta = client.get("/openapi.json")

    assert "cdn.jsdelivr.net" in respuesta.headers["Content-Security-Policy"]


def test_request_id_se_expone_para_trazabilidad():
    respuesta = client.get("/health")

    assert len(respuesta.headers["X-Request-ID"]) == 36
