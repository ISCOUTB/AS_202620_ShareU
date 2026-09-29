# 2. Restricciones arquitectónicas

- El backend se implementa inicialmente con Python y FastAPI.
- El frontend se implementa con Next.js (ver ADR 0005), cumpliendo la
  restricción de stack del curso (Backend: NestJS/FastAPI — Frontend:
  Flutter/Next.js).
- El proyecto se entrega incrementalmente.
- El despliegue inicial es de dos servicios independientes: backend
  (Render) y frontend (Vercel) — ver ADR 0006 y ADR 0007.
- Los cinco dominios deben conservar fronteras explícitas.
- La persistencia del corte vertical utiliza SQLite y la biblioteca estándar
  de Python para mantener el alcance pequeño.
- Las pruebas se ejecutan con `pytest`, incluida una prueba de contrato
  sobre `docs/api/openapi.yaml` (ver ADR y ficha S7).
- La integración continua se realiza con GitHub Actions.
- Las decisiones arquitectónicas se registran mediante ADR.
- Toda API pública se especifica primero como contrato ejecutable
  (OpenAPI/AsyncAPI) versionado en `docs/api/`, y ese contrato se verifica
  con una prueba de contrato en el pipeline.
- **Restricción de costo:** el despliegue debe mantenerse en **USD 0/mes**
  y **sin tarjeta de crédito** en ningún proveedor, mientras el proyecto
  sea un ejercicio académico (ver `docs/costos/estimacion-costo.md`). Esta
  restricción es la que descarta alternativas como Railway en ADR 0006.
