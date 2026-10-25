"""Firestore falso en memoria: las pruebas no necesitan credenciales ni red (ADR 0012)."""
import pytest

from app.documentos import repository


class _Documento:
    def __init__(self, datos):
        self._datos = datos

    def to_dict(self):
        return dict(self._datos)


class _Referencia:
    def __init__(self, coleccion, id_):
        self.coleccion, self.id = coleccion, id_


class _Coleccion:
    def __init__(self, datos=None):
        self.datos = datos if datos is not None else {}

    def document(self, id_):
        return _Referencia(self, id_)

    def limit(self, n):
        return _Coleccion(dict(list(self.datos.items())[:n]))

    def order_by(self, campo):
        return _Coleccion(dict(sorted(self.datos.items(), key=lambda par: par[1][campo])))

    def stream(self):
        return [_Documento(v) for v in self.datos.values()]


class _Lote:
    def __init__(self):
        self.operaciones = []

    def set(self, referencia, datos):
        self.operaciones.append((referencia, datos))

    def commit(self):
        for referencia, datos in self.operaciones:
            referencia.coleccion.datos[referencia.id] = dict(datos)


class _Cliente:
    def __init__(self):
        self.colecciones = {}

    def collection(self, nombre):
        return self.colecciones.setdefault(nombre, _Coleccion())

    def batch(self):
        return _Lote()


@pytest.fixture(autouse=True)
def firestore_falso(monkeypatch):
    cliente = _Cliente()
    monkeypatch.setattr(repository, "_cliente", lambda: cliente)
    monkeypatch.setattr(repository, "_inicializado", False)
    return cliente
