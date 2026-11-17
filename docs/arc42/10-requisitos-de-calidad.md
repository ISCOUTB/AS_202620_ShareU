# 10. Requisitos de calidad

## 10.1 Escenario prioritario: búsqueda de material

| Elemento | Descripción |
|---|---|
| Fuente del estímulo | Estudiante universitario |
| Estímulo | Necesita encontrar material y combina criterios (materia, tipo, palabra clave…) |
| Artefacto | Interfaz web y módulo de búsqueda |
| Entorno | Uso normal; backend con caché tibia; Firestore disponible |
| Respuesta | Resultados relevantes en una sola solicitud, ordenados por calificación |
| Medida de respuesta | p95 ≤ 500 ms; tasa de error < 1 %; ≤ 0,1 lecturas Firestore/búsqueda con caché |

El presupuesto funcional de ≤ 3 interacciones se conserva como prueba de usabilidad
(`tests/test_escenario_usabilidad.py`), pero la medida **del sistema** es latencia y costo de
lecturas, porque es operacional y reproducible (ADR 0016).

## 10.2 Umbral, método y resultado

| Atributo | Umbral | Método | Línea base | Resultado con caché | Veredicto |
|---|---|---|---|---|---|
| Latencia p95 | ≤ 500 ms | `scripts/medicion/bench_busqueda.py`, 300 solicitudes, 20 de calentamiento, concurrencia 10, ASGI en proceso | 72,15 ms | 67,54 ms | **Cumple** |
| Tasa de error | < 1 % | Misma corrida; cuenta respuestas no 2xx y excepciones | 0 % | 0 % | **Cumple** |
| Lecturas Firestore/búsqueda | ≤ 0,1 | Contador del Firestore falso | 1,0 | 0,07 | **Cumple** |

Artefactos: [`s10-linea-base-sin-cache.md`](../evidencia/mediciones/s10-linea-base-sin-cache.md)
(sin caché) y [`s14-local-asgi.md`](../evidencia/mediciones/s14-local-asgi.md) (con caché), con sus
JSON. La línea base se obtiene con `--sin-cache`, sin cambiar el código.

**Límite de validez:** el modo ASGI no incluye red ni Firestore reales; el número es un **límite
inferior** y no se extrapola al servidor del laboratorio. La corrida con `--url` queda pendiente
mientras el despliegue responda 404.

## 10.3 Otros escenarios medibles

| Atributo | Escenario | Medida | Evidencia |
|---|---|---|---|
| Usabilidad | Estudiante busca un documento concreto | ≤ 3 interacciones (campos + clic) | `test_escenario_usabilidad.py`, `medicion-usabilidad.md` |
| Disponibilidad | Firestore caído o lento | 503 en ≤ 3 × 2 s, sin colgar el proceso; `/health` sigue | `test_timeout_se_reporta_como_error_de_persistencia` |
| Consistencia | Reintento de publicación | Mismo documento, sin segundo evento | `test_repetir_la_misma_clave_no_duplica`, `test_reintentar_la_publicacion_no_emite_un_segundo_evento` |
| Consistencia | Duplicado del evento | Una sola entrada en la bandeja | `test_un_duplicado_no_crea_dos_entradas_de_revision` |
| Seguridad | Acceso sin token | 401 con token inválido; 503 sin configuración | `test_token_incorrecto_devuelve_401`, `test_sin_token_configurado_la_escritura_esta_apagada` |
| Mantenibilidad | Cruce de fronteras | Cero imports de repositorios ajenos | `test_modulos_solo_se_hablan_por_service` |

## 10.4 Cómo se defiende

1. El umbral está en **un solo lugar** (esta sección) y la herramienta lo repite.
2. Cualquiera puede reproducir la medición con el comando documentado en
   `docs/evidencia/s14-medicion.md`.
3. La comparación es justa: misma herramienta, mismos datos, misma concurrencia; solo cambia el TTL.
4. La evidencia negativa también se publica: el *stampede* de la caché fría (21 lecturas en 300
   búsquedas) se reconoce como limitación y no se esconde.
