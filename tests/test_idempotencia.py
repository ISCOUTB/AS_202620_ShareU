"""Publicación idempotente y reintentos del borde de persistencia (S11)."""
import time

import pytest
from fastapi.testclient import TestClient

from app.documentos import repository
from app.main import app

client = TestClient(app)

CUERPO = {
    "titulo": "Parcial de Arquitectura",
    "universidad": "Universidad Nacional",
    "carrera": "Ingeniería de Sistemas",
    "materia": "Arquitectura de Software",
    "tipo": "Parcial",
    "autor": "Nicolás",
    "calificacion": 4.4,
    "palabras_clave": "parcial arquitectura adr",
}
TOKEN = "token-de-prueba-123"


def _publicar(clave: str, cuerpo: dict | None = None, token: str = TOKEN):
    return client.post(
        "/documentos",
        json=cuerpo or CUERPO,
        headers={"Idempotency-Key": clave, "X-Admin-Token": token},
    )


def test_publicacion_crea_el_documento(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    respuesta = _publicar("idempotencia-crea-0001")

    assert respuesta.status_code == 201
    assert respuesta.json()["titulo"] == CUERPO["titulo"]
    assert "idempotency_key" not in respuesta.json()


def test_repetir_la_misma_clave_no_duplica(monkeypatch, firestore_falso):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    primera = _publicar("idempotencia-repite-0001")
    segunda = _publicar("idempotencia-repite-0001")

    assert primera.status_code == 201
    assert segunda.status_code == 200
    assert primera.json()["id"] == segunda.json()["id"]
    assert len(firestore_falso.collection("documentos").datos) == 6


def test_misma_clave_con_otro_cuerpo_devuelve_409(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)
    _publicar("idempotencia-conflicto-0001")
    otro = {**CUERPO, "titulo": "Otro título"}

    respuesta = _publicar("idempotencia-conflicto-0001", cuerpo=otro)

    assert respuesta.status_code == 409


def test_sin_token_configurado_la_escritura_esta_apagada(monkeypatch):
    monkeypatch.delenv("SHAREU_ADMIN_TOKEN", raising=False)

    respuesta = _publicar("idempotencia-sin-token-0001")

    assert respuesta.status_code == 503


def test_token_incorrecto_devuelve_401(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    respuesta = _publicar("idempotencia-token-malo-0001", token="otro-token")

    assert respuesta.status_code == 401


def test_la_publicacion_queda_visible_en_la_busqueda(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)
    client.get("/busqueda/documentos")  # llena la caché

    creado = _publicar("idempotencia-visible-0001", cuerpo={**CUERPO, "materia": "Compiladores"})
    busqueda = client.get("/busqueda/documentos", params={"materia": "Compiladores"})

    assert creado.status_code == 201
    assert busqueda.json()["total"] == 1
    assert busqueda.json()["resultados"][0]["id"] == creado.json()["id"]


def test_reintentos_recuperan_un_fallo_transitorio():
    intentos = {"n": 0}

    def operacion():
        intentos["n"] += 1
        if intentos["n"] < 3:
            raise RuntimeError("fallo transitorio")
        return "ok"

    assert repository._con_reintentos(operacion, intentos=3, espera=0) == "ok"
    assert intentos["n"] == 3


def test_timeout_se_reporta_como_error_de_persistencia():
    def lenta():
        time.sleep(0.2)
        return "tarde"

    with pytest.raises(repository.ErrorPersistencia):
        repository._con_reintentos(lenta, intentos=1, espera=0, timeout=0.01)


def test_reservar_id_salta_un_id_que_otro_escritor_tomo(firestore_falso):
    """`create` es atómico: si el id está ocupado se prueba el siguiente.

    Es lo que sostiene la garantía fuerte de «publicar documento» sin
    autoincremento (docs/datos/consistencia.md, ADR 0011).
    """
    coleccion = firestore_falso.collection("documentos")
    coleccion.datos["6"] = {"id": 6, "titulo": "Tomado por otro escritor"}

    nuevo = repository._reservar_id_y_crear(coleccion, {"titulo": "Nuevo"}, 6)

    assert nuevo["id"] == 7
    assert coleccion.datos["6"]["titulo"] == "Tomado por otro escritor"
    assert coleccion.datos["7"]["titulo"] == "Nuevo"


def test_dos_publicaciones_no_repiten_id(monkeypatch, firestore_falso):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    primera = _publicar("idempotencia-unica-0001")
    segunda = _publicar("idempotencia-unica-0002", cuerpo={**CUERPO, "titulo": "Otro"})

    assert primera.json()["id"] != segunda.json()["id"]
    assert len(firestore_falso.collection("documentos").datos) == 7
