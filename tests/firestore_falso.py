"""Doble de prueba de Firestore en memoria.

Vive fuera de `conftest.py` para que el script de medición
(`scripts/medicion/bench_busqueda.py`) pueda reutilizarlo sin depender de
pytest. No implementa índices, cuotas ni transacciones reales: solo la parte
del cliente que el repositorio usa (leer, consultar, `create` y `batch`).
"""
from google.api_core.exceptions import AlreadyExists


class Documento:
    def __init__(self, datos):
        self._datos = datos

    def to_dict(self):
        return dict(self._datos)


class Referencia:
    def __init__(self, coleccion, id_):
        self.coleccion, self.id = coleccion, id_

    def get(self):
        datos = self.coleccion.datos.get(self.id)
        return Documento(datos) if datos is not None else None

    def create(self, datos):
        """Crea solo si el id está libre; si no, falla como Firestore real."""
        if self.id in self.coleccion.datos:
            raise AlreadyExists(f"documento {self.id} ya existe")
        self.coleccion.datos[self.id] = dict(datos)
        self.coleccion.contar_escritura()

    def set(self, datos):
        self.coleccion.datos[self.id] = dict(datos)
        self.coleccion.contar_escritura()


class Coleccion:
    def __init__(self, datos=None, cliente=None):
        self.datos = datos if datos is not None else {}
        self.cliente = cliente

    def document(self, id_):
        return Referencia(self, id_)

    def limit(self, n):
        return Coleccion(dict(list(self.datos.items())[:n]), self.cliente)

    def where(self, campo, operador, valor):
        if operador != "==":
            raise NotImplementedError(f"Operador no soportado: {operador}")
        return Coleccion(
            {
                clave: datos
                for clave, datos in self.datos.items()
                if datos.get(campo) == valor
            },
            self.cliente,
        )

    def order_by(self, campo):
        return Coleccion(
            dict(sorted(self.datos.items(), key=lambda par: par[1][campo])),
            self.cliente,
        )

    def stream(self):
        self._contar_lectura()
        return [Documento(v) for v in self.datos.values()]

    def _contar_lectura(self):
        cliente = getattr(self, "cliente", None)
        if cliente is not None:
            cliente.lecturas += 1

    def contar_escritura(self):
        cliente = getattr(self, "cliente", None)
        if cliente is not None:
            cliente.escrituras += 1


class Lote:
    def __init__(self, cliente=None):
        self.operaciones = []
        self.cliente = cliente

    def set(self, referencia, datos):
        self.operaciones.append((referencia, datos))

    def commit(self):
        for referencia, datos in self.operaciones:
            referencia.coleccion.datos[referencia.id] = dict(datos)
        if self.cliente is not None:
            self.cliente.escrituras += 1


class Cliente:
    def __init__(self):
        self.colecciones = {}
        self.lecturas = 0
        self.escrituras = 0

    def collection(self, nombre):
        coleccion = self.colecciones.setdefault(nombre, Coleccion())
        coleccion.cliente = self
        return coleccion

    def batch(self):
        return Lote(self)
