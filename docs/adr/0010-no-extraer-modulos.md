# ADR 0010: No extraer ningún módulo a un servicio independiente (por ahora)

- **Estado:** Propuesto (pasa a Aceptado cuando el equipo lo apruebe)
- **Fecha:** octubre de 2026
- **Aspecto relacionado:** Usabilidad / Disponibilidad / Escalabilidad
- **Origen:** Evidencia S11 — [`docs/resiliencia/modos-de-fallo.md`](../resiliencia/modos-de-fallo.md)

## Contexto

El ADR 0001 prevé «una ruta futura para extraer un módulo si aparece una necesidad real» y su regla 5 exige un
ADR con evidencia para hacerlo. La única llamada de red del sistema es frontend → API; todo lo demás (por ejemplo
`busqueda` → `documentos`) es una llamada de función dentro del mismo proceso.

El candidato más plausible a extraer es **`busqueda`**: es el flujo del escenario prioritario, es de solo lectura
y es el que más tráfico recibiría. Los demás módulos no tienen carga ni ciclo de cambio propios (`usuarios`,
`calificaciones` y `administracion` solo exponen `/ping` o una métrica en memoria).

## Decisión

**No se extrae ningún módulo.** El sistema sigue como monolito modular de un solo despliegue.

## Opciones evaluadas

### A. No extraer — elegida

- Ventaja: la llamada `busqueda` → `documentos` sigue siendo una función; no aparecen los modos de fallo de red
  (no responde, responde tarde, responde dos veces) dentro del backend.
- Ventaja: un solo despliegue en Render Free, costo USD 0 y sin tarjeta (`docs/arc42/arc42.md` §2).
- Ventaja: `tests/test_fronteras.py` ya hace ejecutable la frontera, de modo que extraer más adelante sigue siendo posible.
- Desventaja: no se puede escalar `busqueda` por separado; un error no controlado en un módulo puede afectar al proceso entero.
- Consecuencia: se acepta, porque hoy no hay carga que lo justifique (5 documentos de ejemplo, respuesta en milisegundos).

### B. Extraer `busqueda` como servicio propio — descartada por ahora

- Ventaja: escalado independiente del flujo más usado y aislamiento de fallos.
- Desventaja: `busqueda` necesita datos de `documentos` (y después de `calificaciones`): habría que llamarlos por red.
  Esa llamada heredaría los tres modos de fallo de la tabla de S11, con sus timeouts, reintentos e idempotencia, para
  proteger un flujo que hoy funciona.
- Desventaja: un segundo servicio comparte las 750 horas gratuitas de Render y duplica despliegue, CI y logs
  para un equipo pequeño.
- Consecuencia: se descarta hasta que se cumpla algún criterio de reapertura.

## Criterios de reapertura

Se reabre este ADR si se cumple alguno (umbrales propuestos; el equipo los ajusta al aprobarlo):

1. **Carga:** el p95 de `duration_ms` de `GET /busqueda/documentos` (logs JSON) supera 500 ms de forma sostenida, con el
   catálogo real, y el cuello de botella es el cómputo del módulo y no la base de datos.
2. **Ciclo de cambio:** un módulo necesita desplegarse con una frecuencia que bloquea a los demás.
3. **Aislamiento:** un fallo de un módulo ha tumbado `/health` de todo el sistema más de una vez.
4. **Costo:** existe un plan con más de un servicio, sin costo y sin tarjeta.

Si se reabre, el nuevo ADR debe incluir la tabla de modos de fallo de la nueva llamada de red, su diseño de
idempotencia y la actualización del C4 nivel 2.

## Consecuencias

### Positivas
- Sin nuevas llamadas de red internas ni nuevos modos de fallo dentro del backend.
- Mismo despliegue, mismo costo.

### Negativas
- Escalado y aislamiento de fallos solo a nivel de todo el monolito.
- Hay que vigilar el acoplamiento entre módulos (ya cubierto por `tests/test_fronteras.py`).

## Trazabilidad

`docs/aspectos/aspectos.md` → este ADR → `docs/resiliencia/modos-de-fallo.md`, `docs/arc42/arc42.md` §11 →
`app/frontend/lib/api.ts`, `tests/test_resiliencia.py`, `tests/test_fronteras.py`.
