# ADR 0012: Persistencia en Firestore (Firebase) en lugar de SQLite

- **Estado:** Propuesto (pasa a Aceptado cuando el equipo lo apruebe)
- **Fecha:** septiembre de 2026
- **Aspecto relacionado:** Disponibilidad / Modificabilidad
- **Reemplaza:** la parte de persistencia del ADR 0006 (SQLite sin disco persistente)

## Contexto

SQLite vive dentro del contenedor del backend. En Render Free no hay disco persistente, así que los datos
vuelven a los de ejemplo en cada reinicio o despliegue (README, ADR 0006). El equipo decidió usar Firebase como
base de datos. La restricción de costo sigue siendo USD 0 y sin tarjeta (`docs/arc42/arc42.md` §2): Firestore en el
plan Spark la cumple.

## Decisión

1. La persistencia pasa a **Firestore** (plan Spark), usando `firebase-admin` **solo en el backend**.
2. Solo `app/documentos/repository.py` conoce Firebase. El resto de módulos no cambia: siguen usando
   `documentos.service` (ADR 0001).
3. **El frontend no habla con Firebase.** Sigue consumiendo `GET /busqueda/documentos` (ADR 0002); el contrato
   OpenAPI no cambia.
4. Las reglas de Firestore niegan todo acceso de clientes (`allow read, write: if false;`). El backend accede con
   una cuenta de servicio, que ignora las reglas.
5. La credencial (JSON de la cuenta de servicio) se entrega por la variable `FIREBASE_CREDENTIALS_JSON` en Render y
   en el `.env` local. Nunca se sube al repositorio.
6. Los documentos conservan el campo `id` entero; el id del documento en Firestore es ese mismo número como texto.
7. Las pruebas usan un Firestore falso en memoria (`tests/conftest.py`): no necesitan red ni credenciales, y el CI
   no cambia.

## Alternativas consideradas

### A. Mantener SQLite — descartada
- Ventaja: sin dependencia externa.
- Desventaja: los datos se pierden en cada despliegue de Render Free; no sirve para demostrar calificaciones ni
  usuarios reales.

### B. Firestore consumido directamente desde el frontend — descartada
- Ventaja: menos código de backend.
- Desventaja: rompe el monolito modular (los módulos dejarían de ser dueños de sus datos), duplica en el cliente la
  lógica de filtrado y deja las reglas de seguridad como única defensa. Contradice ADR 0001 y ADR 0002.

### C. Firestore detrás de `documentos/repository.py` — elegida
- Ventaja: el cambio queda en un archivo, tal como anticipaba el ADR 0011 (el motor es barato de revertir).
- Ventaja: los datos sobreviven a reinicios y despliegues, sin costo ni tarjeta.
- Consecuencia: aparece una dependencia externa en el camino de la búsqueda (ver Consecuencias).

### D. Realtime Database — descartada
- Desventaja: consultas y estructura más pobres que Firestore para filtrar por varios campos.

## Consecuencias

### Positivas
- Persistencia real entre despliegues: se resuelve el punto de ruptura que señalaba `docs/costos/estimacion-costo.md`.
- Ningún cambio en módulos, rutas, contrato ni frontend.

### Negativas
- **Nuevo modo de fallo en la búsqueda:** si Firestore no responde, responde tarde o se agota la cuota, la API
  devuelve 5xx. El frontend ya reintenta una vez ante 5xx (`docs/resiliencia/modos-de-fallo.md`).
- **Costo en lecturas:** cada búsqueda lee todos los documentos (el filtrado sigue en `busqueda.service`). El plan Spark
  da 50 000 lecturas al día: con 5 documentos son unas 10 000 búsquedas diarias; con 500, solo 100. Es el criterio que
  activa la caché del §8.7 de arc42.
- **Ids:** Firestore no tiene autoincremento. Para publicar documentos nuevos habrá que generar el id; el ADR 0011
  recomienda en ese momento pasar a ids de texto (id automático de Firestore) y publicar la versión mayor del contrato.
- El Firestore falso de las pruebas no valida índices ni cuotas reales: conviene una prueba manual contra el proyecto real.

## Criterio de reapertura

Reabrir si la cuota gratuita se agota con el uso real, si Firebase exige tarjeta para el plan, o si el equipo
necesita consultas que Firestore no resuelva.

## Trazabilidad

`docs/adr/0006-plataforma-backend-despliegue.md` → este ADR → `app/documentos/repository.py`,
`tests/conftest.py`, `tests/test_repositorio_firestore.py`, `requirements.in` → `docs/arc42/arc42.md` §2, §7, §8.
