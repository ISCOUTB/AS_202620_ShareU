#!/usr/bin/env python
"""Medición reproducible de latencia y costo de lecturas de la búsqueda.

Herramienta del proyecto para S10 (línea base y contraste) y S14 (medición de
atributos de calidad). Mide `GET /busqueda/documentos` con carga concurrente,
varias repeticiones y percentiles, y cuenta cuántas lecturas a Firestore hace
cada búsqueda cuando la caché está encendida o apagada.

Dos entornos:

* **asgi-en-proceso** (por omisión): levanta la app con el transporte ASGI de
  httpx y el Firestore falso de `tests/firestore_falso.py`. No necesita red ni
  credenciales, así que la medición se puede repetir en CI. Declara ese entorno
  en el informe: no mide la red ni Firestore reales.
* **http**: `--url https://api-shareu.iscoutb.dev` mide el servicio desplegado.

Ejemplos:

    python -m scripts.medicion.bench_busqueda --json-out docs/evidencia/mediciones/s14.json
    python -m scripts.medicion.bench_busqueda --sin-cache --etiqueta linea-base
    python -m scripts.medicion.bench_busqueda --url http://127.0.0.1:8000 --etiqueta local-http

Umbral (arc42 §10): p95 <= 500 ms con 10 usuarios concurrentes y tasa de error
< 1%. Con caché, además, <= 0,1 lecturas a Firestore por búsqueda.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]
UMBRAL_P95_MS = 500.0
UMBRAL_ERROR = 0.01
UMBRAL_LECTURAS_POR_BUSQUEDA = 0.1


def _percentil(valores: list[float], p: float) -> float:
    if not valores:
        return 0.0
    ordenados = sorted(valores)
    indice = min(len(ordenados) - 1, max(0, round((p / 100) * (len(ordenados) - 1))))
    return ordenados[indice]


def _parsear() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=None, help="URL del backend desplegado.")
    parser.add_argument("--peticiones", type=int, default=300)
    parser.add_argument("--concurrencia", type=int, default=10)
    parser.add_argument("--repeticiones", type=int, default=5)
    parser.add_argument("--calentamiento", type=int, default=20)
    parser.add_argument(
        "--sin-cache",
        action="store_true",
        help="Línea base: desactiva la caché (TTL 0) sin cambiar el código.",
    )
    parser.add_argument("--etiqueta", default="local-asgi")
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--md-out", default=None)
    return parser.parse_args()


def _preparar_asgi(sin_cache: bool):
    """Importa la app ya con el TTL configurado y sustituye el cliente Firestore."""
    os.environ["SHAREU_CACHE_TTL_SEGUNDOS"] = "0" if sin_cache else "300"
    sys.path.insert(0, str(RAIZ))
    sys.path.insert(0, str(RAIZ / "tests"))
    import httpx

    from app.documentos import repository
    from app.main import app
    from firestore_falso import Cliente

    cliente_falso = Cliente()
    repository._cliente = lambda: cliente_falso
    repository._inicializado = False
    repository._cache = repository._CacheDocumentos()
    # La medición no necesita el log por solicitud: ensuciaría el resultado.
    logging.getLogger("shareu").setLevel(logging.WARNING)
    return app, cliente_falso, httpx


async def _una_pasada(cliente, url, cabeceras, peticiones, concurrencia, params) -> dict:
    cola: asyncio.Queue[int] = asyncio.Queue()
    for indice in range(peticiones):
        cola.put_nowait(indice)
    latencias: list[float] = []
    errores = 0
    inicio = time.perf_counter()

    async def trabajador() -> None:
        nonlocal errores
        while True:
            try:
                cola.get_nowait()
            except asyncio.QueueEmpty:
                return
            t0 = time.perf_counter()
            try:
                respuesta = await cliente.get(url, params=params, headers=cabeceras)
                if respuesta.status_code != 200:
                    errores += 1
            except Exception:
                errores += 1
            latencias.append((time.perf_counter() - t0) * 1000)

    await asyncio.gather(*(trabajador() for _ in range(concurrencia)))
    duracion = time.perf_counter() - inicio
    return {
        "latencias_ms": latencias,
        "errores": errores,
        "duracion_s": duracion,
        "peticiones": peticiones,
    }


async def _medir(args) -> dict:
    params = {"materia": "Programación"}
    cabeceras = {"X-Cliente-Medicion": "bench"}
    peticiones = args.peticiones
    if args.url:
        import httpx

        cliente_falso = None
        transporte = None
        cliente = httpx.AsyncClient(base_url=args.url.rstrip("/"), timeout=30.0)
        url = "/busqueda/documentos"
        entorno = f"http ({args.url})"
    else:
        app, cliente_falso, httpx = _preparar_asgi(args.sin_cache)
        transporte = httpx.ASGITransport(app=app)
        cliente = httpx.AsyncClient(transport=transporte, base_url="http://asgi")
        url = "/busqueda/documentos"
        entorno = "asgi-en-proceso (Firestore falso, sin red)"

    repeticiones = []
    try:
        for _ in range(args.calentamiento):
            await cliente.get(url, params=params, headers=cabeceras)

        for indice in range(args.repeticiones):
            if cliente_falso is not None:
                from app.documentos import repository

                repository.invalidar_cache()
            lecturas_antes = getattr(cliente_falso, "lecturas", 0)
            pasada = await _una_pasada(
                cliente, url, cabeceras, peticiones, args.concurrencia, params
            )
            lecturas = getattr(cliente_falso, "lecturas", 0) - lecturas_antes
            pasada["lecturas_firestore"] = lecturas
            pasada["lecturas_por_peticion"] = round(lecturas / peticiones, 4)
            pasada["repeticion"] = indice + 1
            repeticiones.append(pasada)
    finally:
        await cliente.aclose()

    todas = [valor for pasada in repeticiones for valor in pasada["latencias_ms"]]
    errores = sum(pasada["errores"] for pasada in repeticiones)
    total = sum(pasada["peticiones"] for pasada in repeticiones)
    duracion = sum(pasada["duracion_s"] for pasada in repeticiones)
    lecturas = sum(pasada["lecturas_firestore"] for pasada in repeticiones)

    resultado = {
        "etiqueta": args.etiqueta,
        "fecha": datetime.now(timezone.utc).isoformat(),
        "entorno": entorno,
        "cache": "apagada (TTL 0)" if args.sin_cache else "encendida (TTL 300 s, invalidada por repetición)",
        "commit": os.getenv("GITHUB_SHA", "local"),
        "maquina": {
            "python": platform.python_version(),
            "sistema": platform.platform(),
            "procesadores": os.cpu_count(),
        },
        "carga": {
            "peticiones_por_repeticion": peticiones,
            "repeticiones": args.repeticiones,
            "concurrencia": args.concurrencia,
            "calentamiento": args.calentamiento,
            "endpoint": "GET /busqueda/documentos?materia=Programación",
        },
        "resultado": {
            "peticiones_totales": total,
            "errores": errores,
            "tasa_error": round(errores / total, 4) if total else 1.0,
            "p50_ms": round(_percentil(todas, 50), 2),
            "p95_ms": round(_percentil(todas, 95), 2),
            "p99_ms": round(_percentil(todas, 99), 2),
            "media_ms": round(sum(todas) / len(todas), 2) if todas else 0.0,
            "throughput_rps": round(total / duracion, 2) if duracion else 0.0,
            "lecturas_firestore": lecturas,
            "lecturas_por_busqueda": round(lecturas / total, 4) if total else 0.0,
        },
        "repeticiones_detalle": [
            {
                "repeticion": pasada["repeticion"],
                "p50_ms": round(_percentil(pasada["latencias_ms"], 50), 2),
                "p95_ms": round(_percentil(pasada["latencias_ms"], 95), 2),
                "p99_ms": round(_percentil(pasada["latencias_ms"], 99), 2),
                "errores": pasada["errores"],
                "lecturas_firestore": pasada["lecturas_firestore"],
            }
            for pasada in repeticiones
        ],
        "umbral": {
            "p95_ms": UMBRAL_P95_MS,
            "tasa_error": UMBRAL_ERROR,
            "lecturas_por_busqueda_con_cache": UMBRAL_LECTURAS_POR_BUSQUEDA,
        },
    }
    res = resultado["resultado"]
    cumple = (
        res["p95_ms"] <= UMBRAL_P95_MS
        and res["tasa_error"] < UMBRAL_ERROR
        and (args.sin_cache or res["lecturas_por_busqueda"] <= UMBRAL_LECTURAS_POR_BUSQUEDA)
    )
    resultado["conclusion"] = "cumple" if cumple else "no cumple"
    return resultado


def _markdown(resultado: dict[str, Any]) -> str:
    res = resultado["resultado"]
    filas = "\n".join(
        f"| {d['repeticion']} | {d['p50_ms']} | {d['p95_ms']} | {d['p99_ms']} | "
        f"{d['errores']} | {d['lecturas_firestore']} |"
        for d in resultado["repeticiones_detalle"]
    )
    return f"""# Resultado de medición — {resultado['etiqueta']}

- **Fecha (UTC):** {resultado['fecha']}
- **Entorno:** {resultado['entorno']}
- **Caché:** {resultado['cache']}
- **Commit:** `{resultado['commit']}`
- **Carga:** {resultado['carga']['peticiones_por_repeticion']} peticiones por repetición,
  {resultado['carga']['repeticiones']} repeticiones, {resultado['carga']['concurrencia']} concurrentes,
  {resultado['carga']['calentamiento']} de calentamiento.
- **Endpoint:** `{resultado['carga']['endpoint']}`

| Repetición | p50 (ms) | p95 (ms) | p99 (ms) | Errores | Lecturas Firestore |
|---:|---:|---:|---:|---:|---:|
{filas}

## Resultado agregado

| Métrica | Valor | Umbral |
|---|---:|---|
| p50 | {res['p50_ms']} ms | — |
| p95 | {res['p95_ms']} ms | ≤ {resultado['umbral']['p95_ms']} ms |
| p99 | {res['p99_ms']} ms | — |
| Media | {res['media_ms']} ms | — |
| Tasa de error | {res['tasa_error'] * 100:.2f} % | < 1 % |
| Throughput | {res['throughput_rps']} req/s | — |
| Lecturas Firestore por búsqueda | {res['lecturas_por_busqueda']} | ≤ {resultado['umbral']['lecturas_por_busqueda_con_cache']} con caché |

**Conclusión: {resultado['conclusion']}.**
"""


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = _parsear()
    resultado = asyncio.run(_medir(args))
    texto_md = _markdown(resultado)

    if args.json_out:
        destino = Path(args.json_out)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.md_out:
        destino = Path(args.md_out)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto_md, encoding="utf-8")

    print(texto_md)
    return 0 if resultado["conclusion"] == "cumple" else 1


if __name__ == "__main__":
    raise SystemExit(main())
