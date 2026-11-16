"""Taller de mensajes (S12): contrato, deduplicación, reintentos y fallidos."""
import json
import logging
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient

from app import eventos
from app.administracion import revision
from app.main import _JsonFormatter, app

RAIZ = Path(__file__).resolve().parents[1]
ESQUEMA = json.loads(
    (RAIZ / "docs" / "eventos" / "documento-publicado.schema.json").read_text(
        encoding="utf-8"
    )
)
client = TestClient(app)
TOKEN = "token-eventos-123"

CUERPO = {
    "titulo": "Apuntes de Mensajería",
    "universidad": "Universidad Nacional",
    "carrera": "Ingeniería de Sistemas",
    "materia": "Arquitectura de Software",
    "tipo": "Apuntes",
    "autor": "Dayana",
    "calificacion": 4.6,
}


def _publicar(clave: str):
    return client.post(
        "/documentos",
        json=CUERPO,
        headers={"Idempotency-Key": clave, "X-Admin-Token": TOKEN},
    )


def test_el_evento_cumple_el_contrato_publicado(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    respuesta = _publicar("evento-contrato-0001")
    entrada = revision.listar_revision()[0]
    evento = {
        "event_id": entrada["event_id"],
        "tipo": "documento.publicado",
        "version": 1,
        "ocurrido_en": entrada["recibido_en"],
        "correlation_id": entrada["correlation_id"],
        "payload": {
            "id_documento": entrada["id_documento"],
            "titulo": entrada["titulo"],
            "materia": entrada["materia"],
            "autor": entrada["autor"],
        },
    }

    jsonschema.validate(instance=evento, schema=ESQUEMA)
    assert respuesta.status_code == 201


def test_publicar_entrega_el_evento_al_consumidor(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    creado = _publicar("evento-entrega-0001")

    pendientes = revision.listar_revision()
    assert len(pendientes) == 1
    assert pendientes[0]["id_documento"] == creado.json()["id"]
    assert pendientes[0]["estado"] == "pendiente"
    assert eventos.estadisticas()["procesados"] == 1


def test_un_duplicado_no_crea_dos_entradas_de_revision(monkeypatch):
    """Garantía «al menos una vez»: el consumidor deduplica por event_id."""
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)
    _publicar("evento-duplicado-0001")
    event_id = revision.listar_revision()[0]["event_id"]

    eventos.reenviar(event_id)  # el broker reentrega el mismo mensaje
    eventos.despachar()

    assert len(revision.listar_revision()) == 1
    assert eventos.estadisticas()["duplicados"] == 1


def test_reintentar_la_publicacion_no_emite_un_segundo_evento(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    _publicar("evento-idempotente-0001")
    segunda = _publicar("evento-idempotente-0001")

    assert segunda.status_code == 200
    assert eventos.estadisticas()["publicados"] == 1
    assert len(revision.listar_revision()) == 1


def test_un_fallo_recuperable_se_reintenta_y_termina_bien():
    intentos = {"n": 0}

    def manejador(evento):
        intentos["n"] += 1
        if intentos["n"] == 1:
            raise RuntimeError("consumidor caído")

    eventos.suscribir("prueba.recuperable", manejador, nombre="prueba.recuperable")
    eventos.publicar("prueba.recuperable", {"dato": 1}, correlation_id="corr-1")

    assert eventos.despachar() == 0  # primer intento falla y se reprograma
    assert eventos.estadisticas()["reintentos"] == 1
    assert len(eventos.pendientes()) == 1

    assert eventos.despachar(forzar=True) == 1  # segundo intento funciona
    assert intentos["n"] == 2
    assert eventos.estadisticas()["procesados"] == 1


def test_agotar_los_intentos_manda_el_evento_a_fallidos():
    def siempre_falla(evento):
        raise RuntimeError("servicio no disponible")

    eventos.suscribir("prueba.fallida", siempre_falla, nombre="prueba.fallida")
    eventos.publicar("prueba.fallida", {}, correlation_id="corr-2")

    for _ in range(eventos.MAX_INTENTOS):
        eventos.despachar(forzar=True)

    assert eventos.estadisticas()["fallidos"] == 1
    assert eventos.fallidos()[0]["intentos"] == eventos.MAX_INTENTOS
    assert eventos.pendientes() == []


def test_el_log_de_eventos_permite_seguir_el_mensaje():
    record = logging.LogRecord(
        "shareu.eventos", logging.INFO, __file__, 1, "evento procesado", None, None
    )
    record.event_id = "11111111-1111-1111-1111-111111111111"
    record.correlation_id = "corr-visible"
    record.tipo_evento = "documento.publicado"
    record.intento = 0
    record.estado_evento = "procesado"

    linea = json.loads(_JsonFormatter().format(record))

    assert linea["event_id"] == record.event_id
    assert linea["correlation_id"] == "corr-visible"
    assert linea["tipo_evento"] == "documento.publicado"


def test_los_endpoints_de_eventos_y_revision_responden(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)
    creado = _publicar("evento-endpoints-0001")

    estadisticas = client.get("/administracion/eventos")
    bandeja = client.get(
        "/administracion/revision", headers={"X-Admin-Token": TOKEN}
    )

    assert estadisticas.status_code == 200
    assert estadisticas.json()["garantia"] == "al menos una vez"
    assert bandeja.json()["total"] == 1

    resuelto = client.post(
        f"/administracion/revision/{creado.json()['id']}/resolver",
        headers={"X-Admin-Token": TOKEN},
    )
    assert resuelto.status_code == 200
    assert resuelto.json()["estado"] == "aprobado"
    assert (
        client.get(
            "/administracion/revision", headers={"X-Admin-Token": TOKEN}
        ).json()["total"]
        == 0
    )


def test_la_bandeja_de_revision_sin_token_es_rechazada(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    respuesta = client.get("/administracion/revision")

    assert respuesta.status_code == 401


def test_resolver_sin_token_es_rechazado(monkeypatch):
    monkeypatch.setenv("SHAREU_ADMIN_TOKEN", TOKEN)

    respuesta = client.post("/administracion/revision/1/resolver")

    assert respuesta.status_code == 401


@pytest.mark.parametrize("clave", ["", "corta"])
def test_el_contrato_del_evento_rechaza_payload_incompleto(clave):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance={
                "event_id": "11111111-1111-1111-1111-111111111111",
                "tipo": "documento.publicado",
                "version": 1,
                "ocurrido_en": "2026-11-16T00:00:00+00:00",
                "correlation_id": clave,
                "payload": {"id_documento": 1},
            },
            schema=ESQUEMA,
        )
