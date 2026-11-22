# S14 — Medición final e incorporación de la revisión de pares

## 1. Objetivo

Cerrar el ciclo de S10: repetir la medición con la caché encendida, comparar contra la línea base y
contrastar el resultado con el umbral declarado en arc42 §10. Además, dejar constancia de qué se
corrigió a partir de la revisión de pares y qué sigue abierto.

## 2. Configuración de la corrida

| Elemento | Valor |
|---|---|
| Fecha (UTC) | 2026-11-16T22:52:59 |
| Entorno | ASGI en proceso, Firestore falso, sin red |
| Caché | Encendida, TTL 300 s, invalidada entre repeticiones |
| Carga | 3 repeticiones × 100 solicitudes, concurrencia 10, calentamiento 20 |
| Endpoint | `GET /busqueda/documentos?materia=Programación` |
| Máquina | Python 3.12.16, Windows 11, 16 procesadores |
| Commit | `local` (el hash final se registra al subir) |

Comando:

```bash
python -m scripts.medicion.bench_busqueda --etiqueta local-asgi \
  --json-out docs/evidencia/mediciones/s14-local-asgi.json \
  --md-out docs/evidencia/mediciones/s14-local-asgi.md
```

## 3. Resultado contra el umbral

| Métrica | Línea base (S10) | Con caché (S14) | Umbral | Veredicto |
|---|---:|---:|---:|---|
| p95 | 72,15 ms | **67,54 ms** | ≤ 500 ms | **Cumple** |
| Tasa de error | 0,00 % | **0,00 %** | < 1 % | **Cumple** |
| Lecturas Firestore/búsqueda | 1,00 | **0,07** | ≤ 0,10 con caché | **Cumple** |
| p99 | 79,95 ms | 79,50 ms | — | Informativo |
| Throughput | 175,99 req/s | 188,02 req/s | — | Informativo |

Artefactos: [`mediciones/s14-local-asgi.md`](mediciones/s14-local-asgi.md) y su
[`JSON`](mediciones/s14-local-asgi.json). La comparación usa la misma herramienta, los mismos datos y
la misma concurrencia; la única diferencia es el TTL (0 vs. 300 s).

## 4. Lo que el número significa y lo que no

**Significa:** el código de búsqueda y la caché no introducen una regresión de latencia perceptible
y reducen las lecturas de Firestore ~14×. La lógica medida es la real: router → service →
repository → caché/Firestore.

**No significa:** que el servicio desplegado responda en 67 ms. El modo ASGI no incluye red ni
Firestore reales y la máquina es de desarrollo. El número es un **límite inferior**. La corrida
`--url` contra `https://api-shareu.iscoutb.dev` no se pudo hacer: la URL respondía **HTTP 404** al
2026-11-16. Se declara como pendiente, no se sustituye por una suposición.

**Tampoco significa** que la caché sea perfecta: 21 lecturas en 300 búsquedas muestran el
*stampede* de la caché fría. Sin *single-flight*, varias solicitudes concurrentes leen Firestore a
la vez. Se acepta y se documenta.

## 5. Revisión de pares incorporada

| Hallazgo | Qué se cambió | Estado |
|---|---|---|
| El indicador «≤ 3 interacciones» no era operacional | Se adoptó p95/error/lecturas con herramienta y línea base (ADR 0016) | Cerrado |
| Faltaba infraestructura de despliegue | `Dockerfile`, `app/frontend/Dockerfile`, `docker-compose.yml`, `Dockploy/compose.lab.yaml` | Cerrado; despliegue activo con búsqueda pendiente de credenciales |
| Faltaban ADR de decisiones recientes | ADR 0011–0016 | Cerrado |
| Aspectos e IA en rutas no canónicas | `docs/aspectos.md`, `docs/ia.md` | Cerrado |
| arc42/C4/README describían SQLite, Render y Vercel | Reescritos con Firestore, Dokploy, caché y outbox | Cerrado en documentos |
| El borde backend→Firestore no estaba en modos de fallo | `docs/resiliencia/modos-de-fallo.md` reescrito y probado | Cerrado |
| La bandeja exponía datos sin credencial | `X-Admin-Token` obligatorio; OpenAPI 1.3.0 | Cerrado con prueba |
| `next@14.2.15` deprecado | `14.2.35` | Cerrado en repositorio; build en CI |
| Sin run remoto de CI ni Quality Gate | Workflow completo. Los runs #44–#47 fallaron sin jobs por `secrets` dentro de un `if`; corregido. Los runs `44973782961`, `44973929626` y `44974059013` están en verde y el gate público está en **OK** sobre `75bc601` (0 incidencias) | **Cerrado**; el paso explícito de Sonar queda `skipped` por falta de `SONAR_TOKEN` |
| URLs desplegadas en 404 | Comprobación del 2026-11-21: web 200 y `/health` 200; búsqueda 500 por configuración | **Parcial** (acción humana: cargar credenciales de Firestore) |

La tabla completa, con dueño y riesgo residual, está en arc42 §11.3.

## 6. Reproducción por un tercero

1. Crear el entorno e instalar dependencias.
2. Ejecutar `pytest -q` (debe dar 77 pruebas en verde; no requiere credenciales).
3. Ejecutar los dos comandos de medición de §2 y de `s10-experimento.md`.
4. Comparar los JSON con los publicados; los números pueden variar por máquina, pero el orden de
   magnitud y la relación de lecturas deben mantenerse.

## 7. Conclusión

El umbral se cumple en el entorno medido, con evidencia versionada y límites explícitos. La
afirmación defendible es: «la búsqueda cumple p95, error y costo de lecturas en una corrida local
reproducible; el despliegue y la corrida HTTP están pendientes de verificación». Es más útil —y más
honesto— que un «cumple» sin condiciones.

## 8. Trazabilidad

`docs/aspectos.md` (A2, A8) → ADR 0013, 0016 → `scripts/medicion/bench_busqueda.py` →
`docs/evidencia/mediciones/s14-*` → este documento → arc42 §10, §11 → README.
