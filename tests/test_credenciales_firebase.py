"""Pruebas del cargador de ``FIREBASE_CREDENTIALS_JSON``.

Cubren los formatos con los que la credencial llega desde el panel de
despliegue: JSON en una línea, ``\\n`` simples o dobles, CRLF, comillas
exteriores, Base64 y el caso que devolvía 503 en producción: un PEM al que le
falta el relleno ``=`` (``InvalidData(Invalid padding)``).

La clave es sintética y se genera en memoria: no hay red ni secretos reales.
"""
from __future__ import annotations

import base64
import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from firebase_admin import credentials

from app.documentos.repository import _cargar_cuenta, _credencial, _normalizar_pem


@pytest.fixture(scope="module")
def pem() -> str:
    clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return clave.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")


@pytest.fixture(scope="module")
def cuenta(pem: str) -> dict[str, str]:
    return {
        "type": "service_account",
        "project_id": "shareu-pruebas",
        "private_key_id": "clave-de-prueba",
        "private_key": pem,
        "client_email": "pruebas@shareu-pruebas.iam.gserviceaccount.com",
        "client_id": "1",
        "token_uri": "https://oauth2.googleapis.com/token",
    }


def _una_linea(cuenta: dict[str, str]) -> str:
    return json.dumps(cuenta, separators=(",", ":"))


def _con_clave(cuenta: dict[str, str], clave: str) -> str:
    return _una_linea({**cuenta, "private_key": clave})


def test_sin_variable_devuelve_none(monkeypatch):
    monkeypatch.delenv("FIREBASE_CREDENTIALS_JSON", raising=False)
    assert _cargar_cuenta() is None


def test_json_en_una_linea(monkeypatch, cuenta):
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", _una_linea(cuenta))
    datos = _cargar_cuenta()

    assert datos is not None
    assert datos["private_key"].startswith("-----BEGIN PRIVATE KEY-----")
    assert datos["private_key"].endswith("-----END PRIVATE KEY-----\n")
    credentials.Certificate(datos)


def test_doble_escape_de_saltos(monkeypatch, cuenta):
    """``\\\\n`` (escape doble) también debe terminar en una clave válida."""
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", _una_linea(cuenta).replace("\\n", "\\\\n"))
    credentials.Certificate(_cargar_cuenta())


def test_saltos_crlf(monkeypatch, cuenta):
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", _una_linea(cuenta).replace("\\n", "\\r\\n"))
    credentials.Certificate(_cargar_cuenta())


def test_comillas_exteriores(monkeypatch, cuenta):
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", f"'{_una_linea(cuenta)}'")
    credentials.Certificate(_cargar_cuenta())


def test_pem_sin_relleno_recupera_el_padding(monkeypatch, cuenta):
    """Regresión del 503: sin el ``=`` final, cryptography lanza Invalid padding."""
    monkeypatch.setenv(
        "FIREBASE_CREDENTIALS_JSON", _con_clave(cuenta, cuenta["private_key"].replace("=", ""))
    )

    datos = _cargar_cuenta()

    assert datos is not None
    assert datos["private_key"] == _normalizar_pem(cuenta["private_key"])
    credentials.Certificate(datos)


def test_pem_con_espacios_en_las_lineas(monkeypatch, cuenta):
    monkeypatch.setenv(
        "FIREBASE_CREDENTIALS_JSON",
        _con_clave(cuenta, cuenta["private_key"].replace("\n", "   \n")),
    )
    credentials.Certificate(_cargar_cuenta())


def test_json_completo_en_base64(monkeypatch, cuenta):
    codificado = base64.b64encode(_una_linea(cuenta).encode("utf-8")).decode("ascii")
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", codificado)
    credentials.Certificate(_cargar_cuenta())


def test_private_key_en_base64(monkeypatch, cuenta):
    codificada = base64.b64encode(cuenta["private_key"].encode("utf-8")).decode("ascii")
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", _con_clave(cuenta, codificada))
    credentials.Certificate(_cargar_cuenta())


def test_normalizar_pem_es_idempotente(pem):
    una_vez = _normalizar_pem(pem)
    assert _normalizar_pem(una_vez) == una_vez


def test_clave_corrupta_falla_sin_exponer_el_secreto(monkeypatch, cuenta):
    cuerpo = cuenta["private_key"].splitlines()[1]
    corrupta = cuenta["private_key"].replace(cuerpo, cuerpo[:-8], 1)
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", _con_clave(cuenta, corrupta))

    with pytest.raises(ValueError) as error:
        _credencial()

    mensaje = str(error.value)
    assert "FIREBASE_CREDENTIALS_JSON" in mensaje
    assert cuerpo[:32] not in mensaje


def test_pem_sin_cabeceras_falla_con_mensaje_claro(monkeypatch, cuenta):
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", _con_clave(cuenta, "no-es-un-pem"))

    with pytest.raises(ValueError, match="cabeceras PEM"):
        _cargar_cuenta()


def test_valor_que_no_es_json_ni_base64(monkeypatch):
    monkeypatch.setenv("FIREBASE_CREDENTIALS_JSON", "esto-no-es-una-credencial")

    with pytest.raises(ValueError, match="JSON válido"):
        _cargar_cuenta()
