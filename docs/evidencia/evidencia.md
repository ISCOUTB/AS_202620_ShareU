# Evidencia de revisión de documentos de trazabilidad

## Estado actual

En el repositorio queda **un** PDF de trazabilidad:

- [`ShareU_Trazabilidad.pdf`](ShareU_Trazabilidad.pdf) — resumen de la decisión arquitectónica, el
  corte de búsqueda, el objetivo de usabilidad, los ADR y las pruebas.

El archivo se movió desde `docs/adr/` a `docs/evidencia/` porque es evidencia, no una decisión: los
ADR son los únicos documentos que deben vivir en `docs/adr/` y su nombre debe seguir el patrón
`NNNN-*.md`.

## Nota histórica

Una revisión anterior describió dos PDF con distinto contenido (`ShareU_Trazabilida.pdf` y
`ShareU_Trazabilidad.pdf`). Ese estado ya no corresponde al repositorio actual: hoy solo existe el
segundo. Si se recupera el otro archivo, debe revisarse antes de citarlo y no debe duplicar la
evidencia ya cubierta por los ADR y las mediciones.

## Dónde está la evidencia vigente

- Decisiones: [`../adr/`](../adr/).
- Trazabilidad de aspectos: [`../aspectos.md`](../aspectos.md).
- Rendimiento y costo: [`mediciones/`](mediciones/) y [`s10-experimento.md`](s10-experimento.md),
  [`s14-medicion.md`](s14-medicion.md).
- Fallos, datos, mensajería, amenazas: [`s11-fallos-parciales.md`](s11-fallos-parciales.md),
  [`s12-datos-cache.md`](s12-datos-cache.md), [`s12-taller-mensajes.md`](s12-taller-mensajes.md),
  [`s13-amenazas.md`](s13-amenazas.md).
