"""Persistencia del módulo de documentos usando Firestore (Firebase).

El repositorio es propiedad del módulo documentos y es el único archivo del
proyecto que conoce Firebase (ADR 0012). Otros módulos consumen la interfaz de
servicio y no acceden directamente a esta colección. El frontend nunca habla con
Firebase: pasa siempre por la API.

Desde S12 este repositorio incorpora:

* una **caché de lectura en proceso** con TTL y expiración explícita
  (ADR 0013, arc42 §8.7);
* **invalidación tras escritura**, para que una publicación sea visible en la
  siguiente lectura;
* **reintentos con espera creciente y timeout** en cada llamada a Firestore
  (S11, `docs/resiliencia/modos-de-fallo.md`);
* **idempotencia** de la publicación mediante ``Idempotency-Key``.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturoTimeoutError
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

from google.api_core.exceptions import AlreadyExists

_COLECCION = "documentos"

_UNIVERSIDAD_NACIONAL = "Universidad Nacional"
_UNIVERSIDAD_DEL_NORTE = "Universidad del Norte"
_INGENIERIA_SISTEMAS = "Ingeniería de Sistemas"

# Campos internos o de auditoría que nunca se exponen por la API.
_CAMPOS_INTERNOS = ("idempotency_key", "idempotency_hash", "creado_en")

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

T = TypeVar("T")


class ErrorPersistencia(RuntimeError):
    """Firestore no respondió o falló después de los reintentos configurados."""


class ConflictoIdempotencia(ValueError):
    """La misma clave de idempotencia llegó con un cuerpo distinto."""


class _CacheDocumentos:
    """Caché de lectura en proceso con TTL y contadores observables.

    El dato cacheado es la lista completa de documentos. Se guarda una copia
    para que un consumidor no pueda mutar la caché por accidente. La escritura
    invalida la entrada; el TTL es solo una red de seguridad ante cambios
    hechos por fuera de este proceso (por ejemplo, la consola de Firebase).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._documentos: list[dict[str, Any]] | None = None
        self._expira_en = 0.0
        self._ttl = float(os.getenv("SHAREU_CACHE_TTL_SEGUNDOS", "60"))
        self._hits = 0
        self._misses = 0
        self._invalidaciones = 0

    @property
    def ttl(self) -> float:
        with self._lock:
            return self._ttl

    def configurar_ttl(self, segundos: float) -> None:
        """Ajusta el TTL; se usa en pruebas y en experimentos de medición."""
        with self._lock:
            self._ttl = max(0.0, float(segundos))
            self._documentos = None
            self._expira_en = 0.0

    def obtener(self) -> list[dict[str, Any]] | None:
        with self._lock:
            if self._documentos is None or time.monotonic() >= self._expira_en:
                self._misses += 1
                return None
            self._hits += 1
            return [dict(documento) for documento in self._documentos]

    def guardar(self, documentos: list[dict[str, Any]]) -> None:
        with self._lock:
            self._documentos = [dict(documento) for documento in documentos]
            self._expira_en = time.monotonic() + self._ttl

    def invalidar(self) -> None:
        with self._lock:
            self._documentos = None
            self._expira_en = 0.0
            self._invalidaciones += 1

    def estadisticas(self) -> dict[str, Any]:
        with self._lock:
            restante = None
            if self._documentos is not None:
                restante = round(max(0.0, self._expira_en - time.monotonic()), 3)
            return {
                "ttl_segundos": self._ttl,
                "entradas": 0 if self._documentos is None else len(self._documentos),
                "hits": self._hits,
                "misses": self._misses,
                "invalidaciones": self._invalidaciones,
                "expira_en_segundos": restante,
            }


_cache = _CacheDocumentos()
_lock_inicializacion = threading.Lock()
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


def _reservar_id_y_crear(
    coleccion: Any,
    datos: dict[str, Any],
    primer_id: int,
    *,
    intentos: int = 5,
) -> dict[str, Any]:
    """Crea el documento con el primer id libre, sin sobrescribir (`create`).

    `create()` es atómico en Firestore: si otro escritor tomó ese id, falla con
    `AlreadyExists` y se prueba el siguiente. Es lo que hace fuerte la garantía
    de «publicar documento» bajo concurrencia (docs/datos/consistencia.md),
    sin depender de un autoincremento que Firestore no tiene (ADR 0011).
    """
    for candidato in range(primer_id, primer_id + intentos):
        nuevo = {"id": candidato, **datos}
        referencia = coleccion.document(str(candidato))

        def crear(documento: dict[str, Any] = nuevo, ref: Any = referencia) -> None:
            ref.create(documento)

        try:
            _con_reintentos(crear)
        except AlreadyExists:
            continue
        return nuevo
    raise ErrorPersistencia(
        f"No se pudo reservar un id libre entre {primer_id} y {primer_id + intentos - 1}"
    )


def _con_reintentos(
    operacion: Callable[[], T],
    *,
    intentos: int = 3,
    espera: float = 0.2,
    timeout: float = 2.0,
) -> T:
    """Ejecuta una llamada a Firestore con timeout y reintentos exponenciales.

    Los reintentos cubren "no responde" y "responde tarde" de
    `docs/resiliencia/modos-de-fallo.md`. El timeout evita que una búsqueda
    quede colgada cuando Render o Firestore están degradados.
    """
    ultimo_error: Exception | None = None
    for intento in range(intentos):
        ejecutor = ThreadPoolExecutor(max_workers=1)
        futuro = ejecutor.submit(operacion)
        try:
            return futuro.result(timeout=timeout)
        except FuturoTimeoutError:
            ultimo_error = ErrorPersistencia("Firestore no respondió dentro del tiempo límite")
            futuro.cancel()
        except AlreadyExists:
            # Conflicto de unicidad: lo resuelve el llamador (reserva de id).
            # Reintentar con el mismo id sería inútil.
            raise
        except Exception as error:  # se reintenta solo el borde de persistencia
            ultimo_error = error
        finally:
            ejecutor.shutdown(wait=False, cancel_futures=True)
        if intento + 1 < intentos:
            time.sleep(espera * (2 ** intento))
    raise ErrorPersistencia(
        f"Firestore falló después de {intentos} intentos: {ultimo_error}"
    ) from ultimo_error


def _inicializar() -> None:
    """Carga los datos de ejemplo una vez por proceso, si la colección está vacía."""
    global _inicializado
    if _inicializado:
        return
    with _lock_inicializacion:
        if _inicializado:
            return
        cliente = _cliente()
        coleccion = cliente.collection(_COLECCION)
        existente = _con_reintentos(
            lambda: next(iter(coleccion.limit(1).stream()), None)
        )
        if existente is None:
            lote = cliente.batch()
            for documento in _SEMILLA:
                lote.set(coleccion.document(str(documento["id"])), documento)

            def confirmar() -> None:
                lote.commit()

            _con_reintentos(confirmar)
        _inicializado = True


def listar_documentos(*, usar_cache: bool = True) -> list[dict[str, Any]]:
    """Devuelve los documentos ordenados por id, usando la caché si está vigente."""
    if usar_cache:
        cacheado = _cache.obtener()
        if cacheado is not None:
            return cacheado
    _inicializar()
    coleccion = _cliente().collection(_COLECCION)

    def leer() -> list[dict[str, Any]]:
        return [documento.to_dict() for documento in coleccion.order_by("id").stream()]

    documentos = _con_reintentos(leer)
    publicos = [_publico(documento) for documento in documentos]
    _cache.guardar(publicos)
    return [dict(documento) for documento in publicos]


def _hash_payload(documento: dict[str, Any]) -> str:
    serializado = json.dumps(documento, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _buscar_por_idempotencia(clave: str):
    coleccion = _cliente().collection(_COLECCION)
    return _con_reintentos(
        lambda: next(
            iter(coleccion.where("idempotency_key", "==", clave).limit(1).stream()),
            None,
        )
    )


def _publico(documento: dict[str, Any]) -> dict[str, Any]:
    return {
        clave: valor
        for clave, valor in documento.items()
        if clave not in _CAMPOS_INTERNOS
    }


def crear_documento(
    documento: dict[str, Any], *, idempotency_key: str
) -> tuple[dict[str, Any], bool]:
    """Crea un documento de forma idempotente.

    Devuelve ``(documento, creado)``. Si la clave ya existe con el mismo
    contenido, devuelve el documento existente con ``creado=False``. Si la
    clave existe con otro contenido, lanza ``ConflictoIdempotencia``.

    La escritura invalida la caché de lectura antes de responder, de modo que
    la siguiente búsqueda observa el documento nuevo (ADR 0013).
    """
    if not idempotency_key or len(idempotency_key) < 8:
        raise ValueError("Idempotency-Key debe tener al menos 8 caracteres")

    _inicializar()
    hash_payload = _hash_payload(documento)
    existente = _buscar_por_idempotencia(idempotency_key)
    if existente is not None:
        previo = existente.to_dict()
        if previo.get("idempotency_hash") != hash_payload:
            raise ConflictoIdempotencia(
                "La clave de idempotencia ya se usó con un contenido distinto"
            )
        return _publico(previo), False

    todos = listar_documentos(usar_cache=False)
    primer_id = max((int(item["id"]) for item in todos), default=0) + 1
    nuevo = _reservar_id_y_crear(
        _cliente().collection(_COLECCION),
        {
            **documento,
            "idempotency_key": idempotency_key,
            "idempotency_hash": hash_payload,
            "creado_en": datetime.now(timezone.utc).isoformat(),
        },
        primer_id,
    )
    _cache.invalidar()
    return _publico(nuevo), True


def invalidar_cache() -> None:
    """Invalida la caché de lectura (se invoca tras una escritura)."""
    _cache.invalidar()


def estadisticas_cache() -> dict[str, Any]:
    """Expone el estado de la caché para evidencia y operación."""
    return _cache.estadisticas()
