"""Pruebas de las defensas del banco de medición (S13).

El banco acepta una URL y rutas de salida por línea de comandos. Estas pruebas
fijan el contrato: solo mide hosts locales salvo permiso explícito y solo
escribe dentro de `docs/evidencia/mediciones`.
"""
import pytest

from scripts.medicion.bench_busqueda import _destino_seguro, _url_medible


def test_url_externa_se_rechaza_por_omision(monkeypatch):
    monkeypatch.delenv("SHAREU_BENCH_PERMITIR_REMOTO", raising=False)
    with pytest.raises(SystemExit):
        _url_medible("https://api-shareu.iscoutb.dev")


def test_url_externa_se_acepta_con_permiso_explicito(monkeypatch):
    monkeypatch.setenv("SHAREU_BENCH_PERMITIR_REMOTO", "1")
    assert _url_medible("https://api-shareu.iscoutb.dev/") == "https://api-shareu.iscoutb.dev"


def test_url_local_se_acepta_sin_permiso(monkeypatch):
    monkeypatch.delenv("SHAREU_BENCH_PERMITIR_REMOTO", raising=False)
    assert _url_medible("http://127.0.0.1:8000/") == "http://127.0.0.1:8000"


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://127.0.0.1/x", "sin-esquema"])
def test_url_con_esquema_no_http_se_rechaza(url):
    with pytest.raises(SystemExit):
        _url_medible(url)


def test_salida_dentro_de_mediciones_se_acepta():
    destino = _destino_seguro("docs/evidencia/mediciones/prueba.json")
    assert destino.name == "prueba.json"


@pytest.mark.parametrize(
    "ruta",
    [
        "../fuera.json",
        "docs/evidencia/otro.json",
        "docs/evidencia/mediciones/../../x.md",
        "/etc/passwd.json",
        "C:/Windows/x.json",
        "docs/evidencia/mediciones/x.txt",
        "docs/evidencia/mediciones/.oculto.json",
    ],
)
def test_salida_fuera_de_mediciones_se_rechaza(ruta):
    with pytest.raises(SystemExit):
        _destino_seguro(ruta)
