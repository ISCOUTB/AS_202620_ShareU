"""La documentación se valida igual que el código (S16/S17).

Estas pruebas ejecutan el mismo validador que el workflow: si un enlace local,
un nombre de ADR o una fila de la tabla de aspectos se rompe, el pipeline falla.
"""
from scripts.validar_docs import (
    comprobar_adr,
    comprobar_aspectos,
    comprobar_enlaces,
    comprobar_plantillas,
    comprobar_rutas,
)


def test_rutas_obligatorias_de_la_documentacion():
    assert comprobar_rutas() == []


def test_nombres_de_adr_segun_convencion():
    assert comprobar_adr() == []


def test_enlaces_locales_resuelven():
    errores, revisados = comprobar_enlaces()
    assert errores == []
    assert revisados > 100


def test_tabla_de_aspectos_completa_y_navegable():
    errores, filas = comprobar_aspectos()
    assert errores == []
    assert filas == 10


def test_sin_marcadores_de_plantilla():
    assert comprobar_plantillas() == []
