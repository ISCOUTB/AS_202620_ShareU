# 2. Restricciones arquitectónicas

| # | Restricción | Consecuencia | Dónde se registra |
|---|---|---|---|
| R1 | Backend en **Python + FastAPI** | Módulos, routers, Pydantic y `pytest` como base | ADR 0001 |
| R2 | Frontend en **Next.js (React)** | Consumo por HTTP/JSON; sin lógica de negocio en el cliente | ADR 0005 |
| R3 | **Costo USD 0/mes y sin tarjeta** | Render/Vercel pagos, brokers gestionados y bases con tarjeta quedan fuera | `docs/costos/estimacion-costo.md`, ADR 0006, ADR 0007 |
| R4 | Despliegue en el **servidor del laboratorio con Dokploy y Docker** | Dos contenedores (`api`, `web`) descritos en `Dockploy/compose.lab.yaml`; sin `ports`, sin bind mounts, sin `container_name`, con límites de CPU/memoria | ADR 0006, ADR 0007 |
| R5 | Persistencia en **Firestore (plan Spark)** | El backend usa una cuenta de servicio; no hay SQL ni disco local como fuente de verdad | ADR 0012 |
| R6 | **Una sola instancia** del backend | Caché y outbox en memoria son aceptables; no hay coordinación entre réplicas | ADR 0013, ADR 0015 |
| R7 | Los cinco dominios conservan **fronteras explícitas** | Un módulo no importa el repositorio de otro; el cableado vive en `app/main.py` | ADR 0001, `tests/test_fronteras.py` |
| R8 | **API-first**: el contrato se escribe antes y se verifica | `docs/api/openapi.yaml` es la fuente de verdad; `tests/test_contrato.py` falla si la respuesta no lo cumple | ADR 0004, §8.5 |
| R9 | **CI en GitHub Actions** | `pytest`, contrato, dependencias, medición y SonarCloud condicional | `.github/workflows/tests.yml` |
| R10 | **Decisiones registradas en ADR** | Toda decisión relevante tiene alternativa descartada y consecuencia | `docs/adr/` |
| R11 | **Despliegue honesto** | Las URLs institucionales no se presentan como verificadas mientras respondan 404 | §7, README |
| R12 | **Privacidad por minimización** | Solo se guarda el nombre del autor; no se registran cuerpos ni IPs | `docs/seguridad/amenazas.md` §4 |

## 2.1 Restricciones que el equipo decidió no relajar

- No se usa `*` en CORS ni se deja la escritura abierta «para la demo» (ADR 0014).
- No se presenta el outbox en memoria como mensajería de producción (ADR 0015, `docs/eventos/limites.md`).
- No se declara un umbral de rendimiento «cumplido» sin una corrida reproducible (ADR 0016).

## 2.2 Restricciones del entorno de trabajo

El equipo no dispone de Node.js en todas las máquinas, así que el build de Next.js y `npm audit` se
validan en CI; el lockfile se mantiene a mano cuando hace falta. El despliegue en el laboratorio lo
opera el equipo con Dokploy y no se automatiza desde el repositorio.
