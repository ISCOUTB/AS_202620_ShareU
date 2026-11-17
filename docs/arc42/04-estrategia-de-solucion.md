# 4. Estrategia de solución

La estrategia es **un monolito modular con dependencias externas mínimas**: un solo desplegable de
backend, un frontend separado, Firestore como almacén y dos mecanismos en proceso (caché y outbox)
que resuelven los dos problemas que el volumen y el costo imponen.

## 4.1 Decisiones estructurantes

| Problema | Estrategia | Alternativa descartada | ADR |
|---|---|---|---|
| Fronteras del dominio | Cinco módulos con `router → service → repository`; el cableado vive en `main.py` | Microservicios desde el inicio | 0001 |
| Búsqueda usable | Filtros combinables en una sola solicitud y orden por calificación | Una pantalla por filtro | 0002 |
| Persistencia | Firestore con `firebase-admin`, encapsulado en `documentos/repository.py` | SQLite sin disco persistente | 0012 |
| Identidad de datos | Id entero reservado con `DocumentReference.create()` | UUID o id automático | 0011 |
| Costo de lectura | Caché en proceso con TTL e invalidación por escritura | Ir siempre a Firestore | 0013 |
| Efecto secundario de publicar | Outbox en proceso, entrega al menos una vez, deduplicación y DLQ | Llamada síncrona o broker | 0015 |
| Seguridad del MVP | `X-Admin-Token`, fail-closed, CORS explícito y cabeceras | Escritura abierta o JWT completo | 0014 |
| Cómo saber si cumple | Medición reproducible de p95, error y lecturas | Contar «interacciones» | 0016 |

## 4.2 El flujo del estudiante manda

La búsqueda es el escenario prioritario. Por eso:

1. El frontend hace **una** solicitud con todos los filtros (`GET /busqueda/documentos`).
2. `busqueda.service` pide los documentos a `documentos.service` y filtra en memoria; no hay una
   consulta por filtro ni una llamada por resultado.
3. La caché evita repetir la lectura de Firestore mientras el catálogo no cambie.
4. La invalidación tras publicar garantiza *read-your-writes* en la instancia que publicó.

## 4.3 El efecto secundario no bloquea

Publicar persiste los metadatos y **después** emite `documento.publicado`; el despacho ocurre en
`BackgroundTasks`, cuando la respuesta ya salió. Si la bandeja falla, el documento sigue publicado
y el outbox reintenta. La garantía es al menos una vez y el consumidor deduplica.

## 4.4 Seguridad proporcionada al alcance

No hay usuarios todavía, así que no se finge una autenticación completa: se separa «público» de
«administración» con un token compartido, se falla cerrado si no está configurado y se endurecen
CORS, cabeceras y errores. El ADR 0014 declara que es transitorio.

## 4.5 La evidencia es parte de la estrategia

Cada afirmación de calidad tiene un artefacto: prueba automatizada, ADR, medición JSON/Markdown o
documento de amenazas. La tabla de [`../aspectos.md`](../aspectos.md) es el índice y el criterio de
cierre: una fila sin evidencia es una fila abierta.
