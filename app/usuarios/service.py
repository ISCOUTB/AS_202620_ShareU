"""Servicio del módulo usuarios: registro, autenticación y perfil.

Sigue las fronteras de arquitectura de ADR 0001 y ADR 0011:
- Las contraseñas se almacenan con hash seguro (SHA-256 + salt aleatorio).
- Los tokens de sesión son opacos y aleatorios (secrets.token_urlsafe).
- Para consultar o publicar documentos del usuario, se interactúa únicamente
  con la interfaz pública `app.documentos.service` (ADR 0001, test_fronteras).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import threading
import time
import uuid
from typing import Any

from app.documentos.service import obtener_documentos, registrar_documento

_LOCK = threading.Lock()

# Almacén de usuarios y sesiones en memoria con sincronización a Firestore
# cuando la credencial está configurada (ADR 0012).
_USUARIOS_MEMORIA: dict[str, dict[str, Any]] = {}
_SESIONES_MEMORIA: dict[str, dict[str, Any]] = {}

# Usuarios iniciales de ejemplo vinculados a los autores de los documentos semilla
def _crear_hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt_val = salt or secrets.token_hex(16)
    digest = hashlib.sha256((salt_val + password).encode("utf-8")).hexdigest()
    return digest, salt_val


def _verificar_password(password: str, hash_almacenado: str, salt: str) -> bool:
    digest, _ = _crear_hash_password(password, salt)
    return secrets.compare_digest(digest, hash_almacenado)


# Semilla de usuarios alineada con los autores en app.documentos.repository._SEMILLA
_salt_ana = "salt_ana_123456"
_hash_ana, _ = _crear_hash_password("Password123!", _salt_ana)
_USUARIOS_MEMORIA["ana@utb.edu.co"] = {
    "id": "usr_ana_001",
    "email": "ana@utb.edu.co",
    "nombre": "Ana",
    "universidad": "Universidad Nacional",
    "carrera": "Ingeniería de Sistemas",
    "password_hash": _hash_ana,
    "salt": _salt_ana,
    "creado_en": "2026-11-01T00:00:00Z",
}

_salt_carlos = "salt_carlos_123456"
_hash_carlos, _ = _crear_hash_password("Password123!", _salt_carlos)
_USUARIOS_MEMORIA["carlos@utb.edu.co"] = {
    "id": "usr_carlos_002",
    "email": "carlos@utb.edu.co",
    "nombre": "Carlos",
    "universidad": "Universidad Nacional",
    "carrera": "Ingeniería de Sistemas",
    "password_hash": _hash_carlos,
    "salt": _salt_carlos,
    "creado_en": "2026-11-01T00:00:00Z",
}


def _obtener_cliente_firestore():
    """Intenta obtener el cliente de Firestore si la credencial existe."""
    contenido = (os.getenv("FIREBASE_CREDENTIALS_JSON") or "").strip()
    if not contenido:
        return None
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            if len(contenido) >= 2 and contenido[0] == contenido[-1] and contenido[0] in "\"'":
                contenido = contenido[1:-1].strip()
            datos = json.loads(contenido)
            # Misma reparación que documentos.repository: \\n literal -> salto real.
            if isinstance(datos, dict) and isinstance(datos.get("private_key"), str):
                datos["private_key"] = datos["private_key"].replace("\\n", "\n")
            firebase_admin.initialize_app(credentials.Certificate(datos))
        return firestore.client()
    except Exception as exc:
        logging.getLogger("shareu").warning(
            "Firestore no disponible para usuarios (%s); se usa el almacén en memoria.",
            type(exc).__name__,
        )
        return None


def registrar_usuario(
    email: str,
    password: str,
    nombre: str,
    universidad: str = "Universidad Nacional",
    carrera: str = "Ingeniería de Sistemas",
) -> dict[str, Any]:
    """Registra un nuevo usuario en ShareU."""
    email_limpio = email.strip().lower()
    if not email_limpio or "@" not in email_limpio:
        raise ValueError("El correo electrónico no es válido")
    if len(password) < 6:
        raise ValueError("La contraseña debe tener al menos 6 caracteres")
    if not nombre.strip():
        raise ValueError("El nombre no puede estar vacío")

    with _LOCK:
        # 1. Comprobar en memoria
        if email_limpio in _USUARIOS_MEMORIA:
            raise ValueError("Ya existe una cuenta con este correo electrónico")

        # 2. Comprobar en Firestore si está disponible
        db = _obtener_cliente_firestore()
        if db is not None:
            try:
                doc = db.collection("usuarios").document(email_limpio).get()
                if doc.exists:
                    raise ValueError("Ya existe una cuenta con este correo electrónico")
            except ValueError:
                raise
            except Exception:
                pass

        hash_pwd, salt = _crear_hash_password(password)
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        datos = {
            "id": user_id,
            "email": email_limpio,
            "nombre": nombre.strip(),
            "universidad": universidad,
            "carrera": carrera,
            "password_hash": hash_pwd,
            "salt": salt,
            "creado_en": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        _USUARIOS_MEMORIA[email_limpio] = datos

        if db is not None:
            try:
                db.collection("usuarios").document(email_limpio).set(datos)
            except Exception:
                pass

    return {
        "id": user_id,
        "email": email_limpio,
        "nombre": nombre.strip(),
        "universidad": universidad,
        "carrera": carrera,
    }


def iniciar_sesion(email: str, password: str) -> dict[str, Any]:
    """Valida credenciales y genera un token de sesión."""
    email_limpio = email.strip().lower()

    with _LOCK:
        usuario = _USUARIOS_MEMORIA.get(email_limpio)

        if usuario is None:
            db = _obtener_cliente_firestore()
            if db is not None:
                try:
                    doc = db.collection("usuarios").document(email_limpio).get()
                    if doc.exists:
                        usuario = doc.to_dict()
                        _USUARIOS_MEMORIA[email_limpio] = usuario
                except Exception:
                    pass

        if usuario is None or not _verificar_password(password, usuario["password_hash"], usuario["salt"]):
            raise ValueError("Correo o contraseña incorrectos")

        token = secrets.token_urlsafe(32)
        info_sesion = {
            "token": token,
            "usuario_id": usuario["id"],
            "email": usuario["email"],
            "nombre": usuario["nombre"],
            "universidad": usuario.get("universidad", "Universidad Nacional"),
            "carrera": usuario.get("carrera", "Ingeniería de Sistemas"),
            "creado_en": time.time(),
        }
        _SESIONES_MEMORIA[token] = info_sesion

        db = _obtener_cliente_firestore()
        if db is not None:
            try:
                db.collection("sesiones").document(token).set(info_sesion)
            except Exception:
                pass

    return {
        "token": token,
        "usuario": {
            "id": usuario["id"],
            "email": usuario["email"],
            "nombre": usuario["nombre"],
            "universidad": usuario.get("universidad", "Universidad Nacional"),
            "carrera": usuario.get("carrera", "Ingeniería de Sistemas"),
        },
    }


def obtener_perfil_por_token(token: str) -> dict[str, Any]:
    """Obtiene el perfil del usuario a partir de su Bearer token."""
    with _LOCK:
        sesion = _SESIONES_MEMORIA.get(token)
        if sesion is None:
            db = _obtener_cliente_firestore()
            if db is not None:
                try:
                    doc = db.collection("sesiones").document(token).get()
                    if doc.exists:
                        sesion = doc.to_dict()
                        _SESIONES_MEMORIA[token] = sesion
                except Exception:
                    pass

        if sesion is None:
            raise ValueError("Sesión no válida o expirada")

        return {
            "id": sesion["usuario_id"],
            "email": sesion["email"],
            "nombre": sesion["nombre"],
            "universidad": sesion.get("universidad", "Universidad Nacional"),
            "carrera": sesion.get("carrera", "Ingeniería de Sistemas"),
        }


def cerrar_sesion(token: str) -> None:
    """Invalida un token de sesión."""
    with _LOCK:
        _SESIONES_MEMORIA.pop(token, None)
        db = _obtener_cliente_firestore()
        if db is not None:
            try:
                db.collection("sesiones").document(token).delete()
            except Exception:
                pass


def obtener_documentos_usuario(nombre_usuario: str) -> list[dict[str, Any]]:
    """Consulta los documentos subidos por el usuario mediante la interfaz pública."""
    todos = obtener_documentos()
    nombre_normalizado = nombre_usuario.strip().lower()
    return [
        doc for doc in todos
        if str(doc.get("autor", "")).strip().lower() == nombre_normalizado
    ]


def publicar_documento_usuario(
    nombre_autor: str,
    titulo: str,
    materia: str,
    tipo: str,
    universidad: str,
    carrera: str,
    palabras_clave: str = "",
) -> dict[str, Any]:
    """Permite al usuario autenticado subir un nuevo documento."""
    idempotency_key = f"usr-doc-{uuid.uuid4().hex}"
    doc_payload = {
        "titulo": titulo,
        "universidad": universidad,
        "carrera": carrera,
        "materia": materia,
        "tipo": tipo,
        "autor": nombre_autor,
        "calificacion": 5.0,
        "palabras_clave": palabras_clave,
    }
    documento, _ = registrar_documento(doc_payload, idempotency_key=idempotency_key)
    return documento
