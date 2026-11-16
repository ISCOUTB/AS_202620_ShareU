# ADR 0014: Endurecimiento HTTP y escritura autenticada con credencial administrativa

- **Estado:** Aceptado
- **Fecha:** noviembre de 2026
- **Aspecto relacionado:** Seguridad
- **Origen:** Evidencia S13 (`docs/seguridad/amenazas.md`)

## Contexto

El MVP expone una API pública de solo lectura y, desde S11/S12, una escritura
(`POST /documentos`) y una bandeja de moderación. El módulo `usuarios` todavía no implementa
registro ni sesiones. Si la escritura queda abierta, cualquiera puede insertar material; si la
bandeja queda abierta, cualquiera lee nombres de autores y material pendiente. Al mismo tiempo, el
navegador necesita consumir la API desde otro origen (frontend en otro dominio) y la API sirve
Swagger/ReDoc.

## Decisión

1. **Autorización de escritura:** `POST /documentos` y las rutas de la bandeja de revisión exigen
   `X-Admin-Token`. El valor se compara con `SHAREU_ADMIN_TOKEN` usando
   `secrets.compare_digest` (tiempo constante).
2. **Fail-closed:** si `SHAREU_ADMIN_TOKEN` no está configurado, las rutas protegidas responden
   **503**; no se abren por omisión. Token ausente o distinto → **401**.
3. **CORS explícito:** orígenes de `SHAREU_FRONTEND_ORIGIN` (por defecto los dos de Next.js en
   local); nunca `*`; solo métodos y cabeceras necesarios.
4. **Cabeceras de seguridad** en todas las respuestas: `X-Content-Type-Options: nosniff`,
   `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, `Permissions-Policy` restrictiva,
   `Cross-Origin-Resource-Policy: same-site` y CSP. La CSP es `default-src 'none'` para la API y
   una política acotada para `/docs`, `/redoc` y `/openapi.json`, que necesitan el CDN de Swagger.
5. **HSTS** solo cuando la solicitud llega por HTTPS (`X-Forwarded-Proto`), para no romper el
   desarrollo local.
6. **Correlación:** cada solicitud recibe `X-Request-ID`, se registra en el log estructurado y se
   reutiliza como `correlation_id` del evento que produce.

La credencial administrativa es una medida **transitoria** mientras no exista autenticación de
usuarios; no se presenta como un sistema de identidades.

## Opciones evaluadas

### A. Dejar la escritura abierta hasta implementar usuarios — descartada
- Ventaja: cero fricción para la demo.
- Desventaja: el repositorio es público y la API desplegada también; un `POST` abierto permite
  llenar la colección o inyectar contenido. El riesgo no se compensa con comodidad.

### B. Autenticación completa con JWT y usuarios — pospuesta
- Ventaja: identidad real, roles y auditoría por usuario.
- Desventaja: exige registro, almacenamiento de credenciales, recuperación y pruebas de seguridad;
  es un corte propio, no una mitigación de esta semana. Queda como trabajo futuro y el ADR se
  reabre cuando `usuarios` entre en alcance.

### C. Token compartido con fail-closed — elegida
- Ventaja: una sola variable, sin base de usuarios, suficiente para separar «público» de
  «administración» en el MVP; se puede rotar sin desplegar código.
- Desventaja: no identifica personas (todos los administradores comparten el token), no hay
  revocación individual y el token debe distribuirse por un canal seguro. Se acepta como riesgo
  residual documentado en `docs/seguridad/amenazas.md`.

### D. Solo reglas de Firestore — descartada
- Ventaja: la base ya niega acceso de clientes.
- Desventaja: el backend usa una cuenta de servicio que **ignora** las reglas; la autorización
  tiene que estar en la API, no solo en Firestore.

## Consecuencias

### Positivas
- Una escritura no autorizada no llega a Firestore.
- La bandeja de moderación deja de ser pública.
- Las cabeceras y el CORS reducen clickjacking, sniffing y uso desde orígenes ajenos.

### Negativas
- Un token compartido no permite saber **quién** publicó o resolvió; el log solo tiene
  `request_id` y `correlation_id`. Aceptado hasta que exista `usuarios`.
- Rotar el token exige actualizar Dokploy y a los administradores.
- La CSP de `/docs` permite `'unsafe-inline'` por la interfaz de Swagger; está acotada a esas
  rutas y no aplica a la API.

## Trazabilidad

`docs/aspectos.md` (A5) → este ADR → `app/seguridad/autenticacion.py`,
`app/documentos/router.py`, `app/administracion/router.py`, `app/main.py` →
`tests/test_seguridad.py`, `tests/test_idempotencia.py`, `tests/test_eventos.py` →
`docs/seguridad/amenazas.md` → arc42 §8.8, §11.
