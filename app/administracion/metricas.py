"""Métrica consultable ligada al escenario de usabilidad (docs/aspectos/aspectos.md).

El escenario prioritario exige que un estudiante encuentre material relevante
combinando criterios en una sola solicitud. Esta métrica cuenta cuántas
búsquedas se ejecutan y cuántas terminan sin resultados, que es el indicador
más cercano al costo de interacción real del flujo: una búsqueda sin
resultados obliga al estudiante a una interacción adicional para reformular,
lo que erosiona el presupuesto de "3 interacciones o menos".

Implementación en memoria: suficiente para el corte vertical actual (un solo
proceso, sin necesidad de infraestructura adicional). Si el despliegue pasa a
tener más de una réplica, este contador deja de ser preciso y debe migrarse a
un backend compartido (ver docs/adr — decisión pendiente si se escala).
"""
from __future__ import annotations

from threading import Lock

_lock = Lock()
_total_busquedas = 0
_busquedas_sin_resultados = 0


def registrar_busqueda(*, total_resultados: int) -> None:
    global _total_busquedas, _busquedas_sin_resultados
    with _lock:
        _total_busquedas += 1
        if total_resultados == 0:
            _busquedas_sin_resultados += 1


def obtener_metricas() -> dict:
    with _lock:
        total = _total_busquedas
        sin_resultados = _busquedas_sin_resultados
    tasa_sin_resultados = (sin_resultados / total) if total else 0.0
    return {
        "escenario": "usabilidad — busqueda combinada en <=3 interacciones (docs/aspectos/aspectos.md)",
        "total_busquedas": total,
        "busquedas_sin_resultados": sin_resultados,
        "tasa_busquedas_sin_resultados": round(tasa_sin_resultados, 4),
    }
