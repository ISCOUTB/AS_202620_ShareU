"""Pruebas del repositorio de documentos sobre Firestore (con cliente falso)."""
from app.documentos import repository


def test_primera_lectura_carga_los_datos_de_ejemplo():
    documentos = repository.listar_documentos()

    assert [d["id"] for d in documentos] == [1, 2, 3, 4, 5]
    assert documentos[0]["titulo"] == "Taller de Python"


def test_cargar_los_datos_de_ejemplo_es_idempotente(firestore_falso, monkeypatch):
    repository.listar_documentos()
    monkeypatch.setattr(repository, "_inicializado", False)  # simula otro proceso
    documentos = repository.listar_documentos()

    assert len(documentos) == 5
    assert len(firestore_falso.collection("documentos").datos) == 5


def test_no_sobrescribe_una_coleccion_con_datos(firestore_falso):
    firestore_falso.collection("documentos").datos["9"] = {"id": 9, "titulo": "Propio"}
    documentos = repository.listar_documentos()

    assert [d["id"] for d in documentos] == [9]
