# 11. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Acoplamiento entre módulos | Alto | Revisar dependencias y usar interfaces de servicio |
| SQLite no escala indefinidamente | Medio | Sustituir persistencia cuando el volumen lo justifique |
| Sin autenticación completa en este corte | Alto | Implementar control de acceso en siguientes incrementos |
| Sin almacenamiento real de archivos | Medio | Integrar servicio de archivos en un corte posterior, síncrono (ADR 0004) |
| Caché aún no implementada | Medio | Medir antes de introducirla y documentar la política de invalidación |
| Sin cola/outbox para notificaciones todavía | Medio | Implementar antes de construir el flujo de correo (ADR 0004) |
| Contrato de API sin generación automática de cliente/stub | Bajo | Evaluar generador (openapi-generator u otro) en un corte posterior |
