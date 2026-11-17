# Aspectos de calidad y trazabilidad — ShareU

Este es el archivo contractual (`/docs/aspectos.md`). Una fila por aspecto, con las ocho columnas
del curso: **ID · Aspecto · Requisito · C4 · ADR · Código · Pruebas · Evidencia**. Cada celda
apunta a un artefacto real del repositorio; una fila con huecos es una fila que no se puede
defender.

## Idea del proyecto

ShareU es una plataforma web para estudiantes universitarios. Permite compartir y encontrar
apuntes, ejercicios, talleres, parciales y otros documentos organizados por universidad, carrera y
materia.

## Escenario prioritario: usabilidad de la búsqueda

| Elemento | Descripción |
|---|---|
| **Fuente del estímulo** | Un estudiante universitario que utiliza ShareU |
| **Estímulo** | Necesita encontrar material académico específico y combina criterios de búsqueda |
| **Artefacto** | Interfaz web y módulo de búsqueda |
| **Entorno** | Uso normal desde computador o celular; backend con caché tibia |
| **Respuesta** | El sistema devuelve resultados relevantes sin navegar entre pantallas ni aplicar filtros por separado |
| **Medida de respuesta** | ≤ 3 interacciones para llegar al resultado (prueba funcional) y, para el sistema, **p95 ≤ 500 ms**, **error < 1 %** y **≤ 0,1 lecturas Firestore/búsqueda** con caché (S10/S14) |

El presupuesto de interacciones se conserva como prueba funcional, pero el reto de S10 se mide con
latencia y costo de lecturas porque es un indicador operacional y reproducible (ADR 0016).

## Tabla de trazabilidad

| ID | Aspecto | Requisito | C4 | ADR | Código | Pruebas | Evidencia |
|---|---|---|---|---|---|---|---|
| A1 | Usabilidad | Encontrar un documento relevante en ≤ 3 interacciones, combinando filtros en una sola solicitud | `web`, `api`, `busqueda` | [ADR 0002](adr/0002-usabilidad-busqueda-en-una-solicitud.md), [ADR 0005](adr/0005-migracion-frontend-nextjs.md) | [`app/frontend/app/page.tsx`](../app/frontend/app/page.tsx), [`app/frontend/lib/api.ts`](../app/frontend/lib/api.ts), [`app/busqueda/`](../app/busqueda/) | [`test_busqueda_combina_filtros`](../tests/test_busqueda.py), [`test_todo_documento_se_encuentra_en_3_interacciones_o_menos`](../tests/test_escenario_usabilidad.py) | [`docs/evidencia/medicion-usabilidad.md`](evidencia/medicion-usabilidad.md) |
| A2 | Rendimiento y costo de lectura | Búsqueda con p95 ≤ 500 ms, error < 1 % y ≤ 0,1 lecturas Firestore/búsqueda con caché | `api`, `busqueda`, `documentos`, `firestore`, `cache` | [ADR 0013](adr/0013-cache-de-lectura-con-invalidacion.md), [ADR 0016](adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) | [`app/documentos/repository.py`](../app/documentos/repository.py) (`_CacheDocumentos`, `listar_documentos`), [`scripts/medicion/bench_busqueda.py`](../scripts/medicion/bench_busqueda.py) | [`test_segunda_lectura_no_va_a_firestore`](../tests/test_cache.py), [`test_el_ttl_expira_la_entrada`](../tests/test_cache.py) | [`s10-linea-base-sin-cache.md`](evidencia/mediciones/s10-linea-base-sin-cache.md), [`s14-local-asgi.md`](evidencia/mediciones/s14-local-asgi.md), [`s14-medicion.md`](evidencia/s14-medicion.md) |
| A3 | Disponibilidad y resiliencia | Si Firestore no responde o responde tarde, la API falla de forma controlada (503) sin colgarse; si el consumidor falla, la publicación no se cae | `api`, `documentos`, `firestore`, `outbox` | [ADR 0004](adr/0004-integracion-sincrona-y-asincrona.md), [ADR 0015](adr/0015-mensajeria-asincrona-con-outbox.md) | [`app/documentos/repository.py`](../app/documentos/repository.py) (`_con_reintentos`), [`app/eventos/outbox.py`](../app/eventos/outbox.py) (`despachar`, `_entregar`) | [`test_reintentos_recuperan_un_fallo_transitorio`](../tests/test_idempotencia.py), [`test_timeout_se_reporta_como_error_de_persistencia`](../tests/test_idempotencia.py), [`test_un_fallo_recuperable_se_reintenta_y_termina_bien`](../tests/test_eventos.py) | [`docs/resiliencia/modos-de-fallo.md`](resiliencia/modos-de-fallo.md), [`docs/evidencia/s11-fallos-parciales.md`](evidencia/s11-fallos-parciales.md) |
| A4 | Consistencia e integridad | Publicar es idempotente (misma clave y cuerpo → mismo documento), dos escritores no comparten id y un duplicado no crea dos entradas de revisión | `api`, `documentos`, `firestore`, `outbox`, `administracion` | [ADR 0011](adr/0011-identidad-de-datos-y-propiedad-por-modulo.md), [ADR 0013](adr/0013-cache-de-lectura-con-invalidacion.md), [ADR 0015](adr/0015-mensajeria-asincrona-con-outbox.md) | [`app/documentos/repository.py`](../app/documentos/repository.py) (`crear_documento`, `_reservar_id_y_crear`), [`app/administracion/revision.py`](../app/administracion/revision.py) | [`test_repetir_la_misma_clave_no_duplica`](../tests/test_idempotencia.py), [`test_dos_publicaciones_no_repiten_id`](../tests/test_idempotencia.py), [`test_un_duplicado_no_crea_dos_entradas_de_revision`](../tests/test_eventos.py) | [`docs/datos/consistencia.md`](datos/consistencia.md), [`docs/eventos/contrato-evento.md`](eventos/contrato-evento.md) |
| A5 | Seguridad | La escritura y la bandeja de moderación exigen credencial; CORS y cabeceras endurecidas; sin secretos versionados | `web`, `api`, `administracion` | [ADR 0014](adr/0014-endurecimiento-http-y-escritura-autenticada.md) | [`app/seguridad/autenticacion.py`](../app/seguridad/autenticacion.py), [`app/main.py`](../app/main.py) (CORS, cabeceras), [`app/documentos/router.py`](../app/documentos/router.py) | [`test_cabeceras_de_endurecimiento`](../tests/test_seguridad.py), [`test_sin_token_configurado_la_escritura_esta_apagada`](../tests/test_idempotencia.py), [`test_la_bandeja_de_revision_sin_token_es_rechazada`](../tests/test_eventos.py), [`test_url_externa_se_rechaza_por_omision`](../tests/test_bench_busqueda.py) | [`docs/seguridad/amenazas.md`](seguridad/amenazas.md), [`docs/seguridad/dependencias.md`](seguridad/dependencias.md) |
| A6 | Mantenibilidad y fronteras | Un módulo no importa archivos internos de otro; cada dato tiene un dueño; no se extrae un servicio sin evidencia | `api`, `usuarios`, `documentos`, `busqueda`, `calificaciones`, `administracion` | [ADR 0001](adr/0001-estilo-arquitectonico.md), [ADR 0008](adr/0008-metrica-tras-interfaz-de-administracion.md), [ADR 0010](adr/0010-no-extraer-modulos.md), [ADR 0011](adr/0011-identidad-de-datos-y-propiedad-por-modulo.md) | [`app/*/service.py`](../app/), [`app/main.py`](../app/main.py) (composición y suscripción) | [`test_modulos_solo_se_hablan_por_service`](../tests/test_fronteras.py), [`test_modulos_montados`](../tests/test_esqueleto.py) | [`docs/ddd/auditoria-violaciones.md`](ddd/auditoria-violaciones.md), [`docs/evidencia/s11-fallos-parciales.md`](evidencia/s11-fallos-parciales.md) |
| A7 | Operabilidad y observabilidad | Pipeline reproducible (pruebas, contrato, dependencias y medición), `/health`, logs JSON por solicitud y métricas consultables ligadas al escenario | `api`, `administracion` | [ADR 0006](adr/0006-plataforma-backend-despliegue.md), [ADR 0016](adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) | [`.github/workflows/tests.yml`](../.github/workflows/tests.yml), [`app/main.py`](../app/main.py) (`_JsonFormatter`, `registrar_solicitud`), [`app/administracion/router.py`](../app/administracion/router.py) | [`test_metricas_cumplen_el_contrato`](../tests/test_contrato.py), [`test_los_endpoints_de_eventos_y_revision_responden`](../tests/test_eventos.py) | [`docs/evidencia/s12-taller-mensajes.md`](evidencia/s12-taller-mensajes.md), [`docs/evidencia/s14-medicion.md`](evidencia/s14-medicion.md) |
| A8 | Costo | Mantener USD 0/mes y sin tarjeta; declarar el punto de ruptura de cada capa gratuita | `web`, `api`, `firestore` | [ADR 0006](adr/0006-plataforma-backend-despliegue.md), [ADR 0007](adr/0007-plataforma-frontend-despliegue.md), [ADR 0012](adr/0012-persistencia-en-firestore.md), [ADR 0013](adr/0013-cache-de-lectura-con-invalidacion.md) | [`docs/costos/estimacion-costo.md`](costos/estimacion-costo.md), [`app/documentos/repository.py`](../app/documentos/repository.py) | [`test_segunda_lectura_no_va_a_firestore`](../tests/test_cache.py) (menos lecturas) | [`s10-linea-base-sin-cache.md`](evidencia/mediciones/s10-linea-base-sin-cache.md), [`s14-local-asgi.md`](evidencia/mediciones/s14-local-asgi.md) |
| A9 | Privacidad | Tratar solo los datos personales necesarios (nombre del autor), no registrar cuerpos ni IPs y declarar la base y la retención | `web`, `api`, `firestore`, `administracion` | [ADR 0014](adr/0014-endurecimiento-http-y-escritura-autenticada.md) | [`app/documentos/repository.py`](../app/documentos/repository.py) (`_CAMPOS_INTERNOS`, `_publico`), [`app/main.py`](../app/main.py) (log sin cuerpo) | [`test_la_bandeja_de_revision_sin_token_es_rechazada`](../tests/test_eventos.py) | [`docs/seguridad/amenazas.md`](seguridad/amenazas.md) §Privacidad |
| A10 | Desacoplamiento temporal | Publicar no espera a la bandeja de revisión; el evento tiene contrato, garantía, deduplicación y DLQ | `documentos`, `outbox`, `administracion` | [ADR 0004](adr/0004-integracion-sincrona-y-asincrona.md), [ADR 0015](adr/0015-mensajeria-asincrona-con-outbox.md) | [`app/eventos/outbox.py`](../app/eventos/outbox.py), [`app/documentos/router.py`](../app/documentos/router.py) (`BackgroundTasks`), [`app/administracion/revision.py`](../app/administracion/revision.py) | [`test_publicar_entrega_el_evento_al_consumidor`](../tests/test_eventos.py), [`test_reintentar_la_publicacion_no_emite_un_segundo_evento`](../tests/test_eventos.py), [`test_agotar_los_intentos_manda_el_evento_a_fallidos`](../tests/test_eventos.py) | [`docs/eventos/contrato-evento.md`](eventos/contrato-evento.md), [`docs/eventos/limites.md`](eventos/limites.md), [`docs/evidencia/s12-taller-mensajes.md`](evidencia/s12-taller-mensajes.md) |

## Tensiones de calidad declaradas

1. **Rendimiento/costo vs. consistencia (A2 vs. A4).** La caché reduce lecturas, pero introduce una
   ventana de inconsistencia entre instancias acotada por el TTL (60 s). Se resuelve con
   invalidación tras escritura y se acepta la ventana entre instancias (ADR 0013).
2. **Disponibilidad vs. integridad (A3 vs. A4).** El outbox permite responder aunque el consumidor
   falle, pero la entrega es al menos una vez; la integridad se recupera con deduplicación por
   `event_id` y por `id_documento` (ADR 0015).
3. **Seguridad vs. usabilidad (A5 vs. A1).** Exigir token a la escritura y a la bandeja protege el
   material, pero agrega un paso operativo; se acepta porque solo afecta al rol administrativo, no
   a la búsqueda pública.

## Decisión arquitectónica relacionada

El escenario de usabilidad motiva el **monolito modular** (ADR 0001): la búsqueda permanece como
módulo independiente y los cambios de persistencia (ADR 0012) o de mensajería (ADR 0015) no
obligan a reescribir el flujo del estudiante.
