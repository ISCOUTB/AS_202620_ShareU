"""Persistencia del módulo de documentos usando Firestore (Firebase).

El repositorio es propiedad del módulo documentos y es el único archivo del
proyecto que conoce Firebase (ADR 0012). Otros módulos consumen la interfaz de
servicio y no acceden directamente a esta colección. El frontend nunca habla con
Firebase: pasa siempre por la API.
"""
from __future__ import annotations

import json
import os
from typing import Any

_COLECCION = "documentos"

_UNIVERSIDAD_NACIONAL = "Universidad Nacional"
_UNIVERSIDAD_DEL_NORTE = "Universidad del Norte"
_INGENIERIA_SISTEMAS = "Ingeniería de Sistemas"

# Datos de ejemplo: se cargan solo si la colección está vacía.
_SEMILLA: list[dict[str, Any]] = [
    {"id": 1, "titulo": "Taller de Python", "universidad": _UNIVERSIDAD_NACIONAL,
     "carrera": _INGENIERIA_SISTEMAS, "materia": "Programación", "tipo": "Taller",
     "autor": "Ana", "calificacion": 4.8, "palabras_clave": "python programación funciones"},
    {"id": 2, "titulo": "Parcial de Bases de Datos", "universidad": _UNIVERSIDAD_NACIONAL,
     "carrera": _INGENIERIA_SISTEMAS, "materia": "Bases de Datos", "tipo": "Parcial",
     "autor": "Carlos", "calificacion": 4.5, "palabras_clave": "sql bases datos parcial"},
    {"id": 3, "titulo": "Apuntes de Arquitectura de Software", "universidad": _UNIVERSIDAD_NACIONAL,
     "carrera": _INGENIERIA_SISTEMAS, "materia": "Arquitectura de Software", "tipo": "Apuntes",
     "autor": "María", "calificacion": 4.7, "palabras_clave": "arquitectura software adr c4"},
    {"id": 4, "titulo": "Ejercicios de Cálculo", "universidad": _UNIVERSIDAD_DEL_NORTE,
     "carrera": _INGENIERIA_SISTEMAS, "materia": "Cálculo", "tipo": "Ejercicios",
     "autor": "Luis", "calificacion": 4.2, "palabras_clave": "calculo derivadas integrales"},
    {"id": 5, "titulo": "Guía de Redes", "universidad": _UNIVERSIDAD_DEL_NORTE,
     "carrera": "Ingeniería de Telecomunicaciones", "materia": "Redes", "tipo": "Guía",
     "autor": "Sofía", "calificacion": 4.6, "palabras_clave": "redes tcp ip protocolos"},
]

_cliente_firestore = None
_inicializado = False


def _credencial():
    from firebase_admin import credentials

    contenido = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if contenido:
        return credentials.Certificate(json.loads(contenido))
    return credentials.ApplicationDefault()  # usa GOOGLE_APPLICATION_CREDENTIALS


def _cliente():
    """Cliente de Firestore. Es el único punto que las pruebas sustituyen."""
    global _cliente_firestore
    if _cliente_firestore is None:
        import firebase_admin
        from firebase_admin import firestore

        if not firebase_admin._apps:
            firebase_admin.initialize_app(_credencial())
        _cliente_firestore = firestore.client()
    return _cliente_firestore


def _inicializar() -> None:
    """Carga los datos de ejemplo una vez por proceso, si la colección está vacía."""
    global _inicializado
    if _inicializado:
        return
    cliente = _cliente()
    coleccion = cliente.collection(_COLECCION)
    if next(iter(coleccion.limit(1).stream()), None) is None:
        lote = cliente.batch()
        for documento in _SEMILLA:
            lote.set(coleccion.document(str(documento["id"])), documento)
        lote.commit()
    _inicializado = True


def listar_documentos() -> list[dict[str, Any]]:
    _inicializar()
    coleccion = _cliente().collection(_COLECCION)
    return [d.to_dict() for d in coleccion.order_by("id").stream()]
