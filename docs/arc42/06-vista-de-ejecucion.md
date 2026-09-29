# 6. Vista de ejecución

## 6.1 Escenario: buscar material (síncrono)

Contrato: [`docs/api/openapi.yaml`](../api/openapi.yaml) — `GET
/busqueda/documentos`. Integración síncrona de extremo a extremo: el
estudiante espera la respuesta HTTP para ver resultados (justificación de
por qué es síncrona, y no asíncrona, en
[`../adr/0004-integracion-sincrona-y-asincrona.md`](../adr/0004-integracion-sincrona-y-asincrona.md)).

| Paso | De → a | Protocolo / formato | Naturaleza |
|---|---|---|---|
| 1 | Estudiante → Aplicación web | HTTPS | Síncrono |
| 2 | Aplicación web → `busqueda.router` | `GET /busqueda/documentos` · JSON/HTTPS | Síncrono |
| 3 | `busqueda.router` → `busqueda.service` | Llamada de función Python | Síncrono, in-process |
| 4 | `busqueda.service` → `documentos.service` | Llamada de función Python (interfaz de servicio, ADR 0001) | Síncrono, in-process |
| 5 | `documentos.service` → `documentos.repository` | Llamada de función Python | Síncrono, in-process |
| 6 | `documentos.repository` → SQLite | SQL | Síncrono |
| 7 | Respuesta: SQLite → ... → Aplicación web | JSON/HTTPS, cuerpo validado contra `ResultadoBusqueda` en el contrato | Síncrono |

```text
Estudiante
    |  HTTPS
    v
Aplicación web
    |  GET /busqueda/documentos  (JSON/HTTPS)
    v
busqueda.router
    |  función Python (in-process)
    v
busqueda.service
    |  función Python (in-process) — interfaz de servicio
    v
documentos.service
    |  función Python (in-process)
    v
documentos.repository
    |  SQL
    v
SQLite
```

Toda la cadena de los pasos 3 a 6 ocurre dentro del mismo proceso — no hay
llamada de red interna que decidir como síncrona o asíncrona; esa decisión
ya la fijó ADR 0001 al declarar un monolito modular. Lo que sí queda sujeto
a la decisión de esta semana es el borde del sistema (pasos 1-2 y las
integraciones de la sección 6.3).

## 6.2 Escenario: sin resultados

Si ningún documento satisface los filtros, la API devuelve HTTP 200 con
`total: 0` y una lista vacía (ver ejemplo `sinResultados` en el contrato).
Esto permite que una interfaz futura muestre un mensaje claro y sugiera
ajustar filtros. Sigue el mismo camino síncrono de la sección 6.1: no hay
una ruta de fallo especial, es una respuesta válida del mismo contrato.

## 6.3 Escenarios futuros: integraciones externas (ver ADR 0004)

Estos flujos todavía no tienen código — se documentan aquí porque la
decisión síncrono/asíncrono que los gobierna ya está tomada y debe guiar la
implementación del próximo corte.

**Publicar un documento (síncrono con almacenamiento):**

```text
Estudiante --HTTPS--> Aplicación web --JSON/HTTPS--> API backend
                                                         |
                                                REST/HTTPS (síncrono)
                                                         v
                                          Almacenamiento de archivos
```

La API espera la confirmación del almacenamiento antes de responder al
estudiante; si falla, no se crea el registro en `documentos` (sin
metadatos huérfanos).

**Notificar por correo (asíncrono, evento/outbox):**

```text
API backend --publica evento (in-process)--> Cola / outbox
                                                    |
                                     entrega asíncrona, con reintentos
                                                    v
                                          Servicio de correo (SMTP/API)
```

La API responde al estudiante sin esperar la entrega del correo. El
contrato de este evento se especificará en AsyncAPI cuando el módulo de
notificaciones entre en alcance de un corte (hoy no hay implementación que
contratar).

## Resumen de naturaleza por integración

| Integración | Naturaleza | Formato | Justificación |
|---|---|---|---|
| Aplicación web → API backend | Síncrona | JSON/HTTPS | El estudiante necesita ver el resultado en la misma interacción |
| `busqueda` → `documentos` | Síncrona, in-process | Llamada de función | Ya resuelto por ADR 0001 (monolito modular) |
| `documentos` → SQLite | Síncrona | SQL | La respuesta HTTP depende del dato leído/escrito |
| API backend → Almacenamiento | Síncrona (futura) | REST/HTTPS | Publicar sin archivo confirmado no es un resultado válido |
| API backend → Correo | Asíncrona (futura) | Evento / outbox | Efecto secundario; no debe acoplar disponibilidad del flujo crítico |
