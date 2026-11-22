# 12. Glosario

| Término | Definición |
|---|---|
| **ShareU** | Plataforma para compartir y encontrar material académico por universidad, carrera y materia |
| **Monolito modular** | Un solo desplegable dividido en módulos de dominio con fronteras explícitas (ADR 0001) |
| **Módulo** | Unidad de código con responsabilidad de un dominio: `router → service → repository` |
| **Interfaz de servicio** | Función pública de `app/<modulo>/service.py`; único canal permitido entre módulos |
| **Corte vertical** | Funcionalidad que atraviesa API, dominio y persistencia hasta un resultado observable |
| **Documento** | Material académico publicado: metadatos en Firestore (el archivo aún no se almacena) |
| **Filtro** | Criterio que reduce resultados: universidad, carrera, materia, tipo, palabra clave, calificación mínima |
| **Firestore** | Base de datos documental de Google Cloud usada como almacén (ADR 0012) |
| **Cuenta de servicio** | Credencial de Firebase que usa el backend; ignora las reglas de cliente |
| **Idempotencia** | Propiedad por la que repetir una operación no cambia el estado ni duplica efectos |
| **`Idempotency-Key`** | Cabecera que identifica un intento de publicación; su repetición devuelve el mismo documento |
| **Caché de lectura** | Copia en memoria de la lista pública de documentos, con TTL e invalidación (ADR 0013) |
| **TTL** | Tiempo de vida de una entrada de caché; por defecto 60 s |
| **Invalidación** | Borrado explícito de la caché tras una escritura para garantizar *read-your-writes* |
| **Outbox** | Registro en proceso de eventos pendientes de entrega (ADR 0015) |
| **Evento** | Mensaje `documento.publicado` con contrato versionado y `event_id` |
| **Al menos una vez** | Garantía de entrega que permite duplicados; el consumidor debe deduplicar |
| **Deduplicación** | Descarte de un evento ya procesado, por `event_id` o por `id_documento` |
| **DLQ** | *Dead-letter queue*: cola de eventos que agotaron los reintentos |
| **Correlación** | `correlation_id` que enlaza una solicitud HTTP con el evento que produjo |
| **Saga** | Secuencia de pasos distribuidos con compensación; **no se usa** porque no hay transacción distribuida |
| **STRIDE** | Modelo de amenazas: suplantación, manipulación, repudio, divulgación, denegación, elevación |
| **ADR** | *Architecture Decision Record*: contexto, decisión, alternativas y consecuencias |
| **C4** | Modelo de documentación por contexto, contenedores, componentes y código |
| **arc42** | Plantilla de documentación de arquitectura usada en este directorio |
| **Contrato de API** | Especificación OpenAPI que la API debe cumplir; se verifica con una prueba |
| **Prueba de contrato** | Prueba que compara una respuesta real con el esquema publicado |
| **p95** | Percentil 95 de latencia: el 95 % de las solicitudes fue más rápido que ese valor |
| **Lecturas por búsqueda** | Promedio de lecturas a Firestore dividido entre búsquedas; mide el costo |
| **Fail-closed** | Ante configuración ausente, la ruta protegida se cierra (503) en vez de abrirse |
| **Dokploy** | Plataforma de despliegue del laboratorio basada en Docker Compose |
| **Healthcheck** | Comprobación periódica de `/health` para reiniciar un contenedor enfermo |
| **`request_id`** | Identificador por solicitud que el middleware devuelve en `X-Request-Id` y usa para correlacionar logs |
| **Quality Gate** | Conjunto de condiciones de SonarCloud sobre el código nuevo; en ShareU está en **OK** sobre `75bc601` (0 incidencias, todas las calificaciones en 1) |
| **Sitio legado** | `shareuwensite-main/`: sitio estático anterior al frontend Next.js (ADR 0005); no se despliega |
| **Matriz de retroalimentación** | Tabla de S17 con cada recomendación recibida, su origen, clasificación y evidencia |
