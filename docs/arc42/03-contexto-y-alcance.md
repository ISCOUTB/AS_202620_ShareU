# 3. Contexto y alcance

## 3.1 Contexto de negocio

| Actor / sistema | Relación con ShareU | Qué espera |
|---|---|---|
| **Estudiante** | Busca, consulta y (en el flujo administrativo) publica material | Encontrar el documento correcto rápido, desde el celular o el computador |
| **Administrador** | Revisa el material publicado y lo aprueba o retira | Ver una bandeja con lo pendiente y resolverla con una acción |
| **Firestore** (externo) | Almacén de metadatos | Disponibilidad y credenciales válidas |
| **GitHub Actions** | Integración continua | Que el pipeline sea reproducible |
| **Dokploy / servidor del laboratorio** | Plataforma de despliegue | Contenedores con healthcheck y límites |

No hay todavía un servicio de correo ni un almacenamiento de archivos en el camino real: existen
como candidatos y se documentan como trabajo futuro, no como componentes activos.

## 3.2 Contexto técnico

```text
Estudiante / Administrador
          |  HTTPS
          v
  Aplicación web (Next.js, contenedor web)
          |  JSON/HTTPS  (timeout 15 s, 1 reintento, X-Request-ID)
          v
  API backend (FastAPI, contenedor api)
     |           |              |
     |           |              +--> outbox en proceso --(evento)--> administración
     |           |
     |           +--> caché de lectura en proceso (TTL 60 s)
     |
     +--> firebase-admin / gRPC-HTTP --> Firestore (externo)
```

| Frontera | Protocolo / formato | Naturaleza | Contrato |
|---|---|---|---|
| Navegador → web | HTTPS | Síncrona | HTML/JS de Next.js |
| web → API | JSON/HTTPS | Síncrona, con timeout y 1 reintento | `docs/api/openapi.yaml` |
| API → Firestore | gRPC/HTTPS vía `firebase-admin` | Síncrona, timeout 2 s, 3 intentos | Modelo de datos en `docs/datos/consistencia.md` |
| documentos → outbox → administración | Llamada de función en proceso (evento) | Asíncrona respecto de la respuesta HTTP | `docs/eventos/documento-publicado.schema.json` |
| API → administrador | Cabecera `X-Admin-Token` en `/documentos` y `/administracion/revision` | Síncrona | ADR 0014 |

## 3.3 Alcance

**Dentro:**

- Búsqueda combinada de documentos y ordenamiento por calificación.
- Publicación idempotente de metadatos con credencial administrativa.
- Evento `documento.publicado` y bandeja de revisión.
- Caché de lectura con invalidación por escritura.
- Contrato OpenAPI, pruebas de contrato, fronteras, idempotencia y eventos.
- Despliegue con Docker/Dokploy y CI.

**Fuera (por ahora):**

- Subida y almacenamiento de archivos (solo metadatos).
- Registro, inicio de sesión y roles de estudiante.
- Calificaciones por usuario (hoy `calificacion` es un atributo del documento).
- Envío de correo.
- Persistencia de la bandeja y del outbox.
- Búsqueda de texto completo en Firestore (hoy se filtra en memoria).
