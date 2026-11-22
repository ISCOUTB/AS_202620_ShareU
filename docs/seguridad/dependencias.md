# Dependencias y cadena de suministro — Evidencia S13

## 1. Qué se ejecuta y cuándo

| Control | Herramienta | Dónde | Bloquea el pipeline | Resultado |
|---|---|---|---|---|
| Vulnerabilidades de Python | `pip-audit -r requirements.in` | Job `dependencias` de `.github/workflows/tests.yml` | **Sí** | `No known vulnerabilities found` en el entorno local (2026-11-16) |
| Vulnerabilidades de Node | `npm audit --json` | Job `dependencias` | **No** (publica artefacto `npm-audit.json`) | Se ejecuta en CI; localmente no hay `npm` instalado |
| Actualizaciones | Dependabot | `.github/dependabot.yml` | No | PR semanales para `pip`, `npm` y GitHub Actions |
| Integridad de instalación | `pip install --require-hashes` | CI y despliegue | **Sí** | `requirements.txt` con hashes |

## 2. Por qué `pip-audit` usa `requirements.in`

`requirements.txt` se instala con `--require-hashes` e incluye dependencias transitivas fijadas. Al
auditar ese archivo, `pip-audit` intenta resolver el árbol y falla con las dependencias sin pin
explícito (por ejemplo `colorama>=0.4`, que llega por `click`). No es una vulnerabilidad: es una
limitación del resolvedor frente a un archivo de hashes. La auditoría se hace sobre
`requirements.in`, que declara los paquetes directos, y la instalación reproducible sigue usando
`requirements.txt`. Ambas cosas cubren riesgos distintos y complementarios.

## 3. Hallazgos y decisiones

| # | Hallazgo | Origen | Decisión | Estado |
|---|---|---|---|---|
| D1 | `next@14.2.15` marcado como deprecado por seguridad en npm | Revisión S9 | Subir a `14.2.35` (última 14.2.x sin marca) en `app/frontend/package.json` y `package-lock.json` | **Corregido**; el build real se valida en CI porque el equipo no tiene Node local |
| D2 | `pip-audit -r requirements.txt` falla por el resolvedor de hashes | CI/local | Auditar `requirements.in`; documentar la diferencia | **Aceptado** |
| D3 | `npm audit` no puede ejecutarse en la máquina del equipo | Local | Se ejecuta en CI y se publica como artefacto; Dependabot cubre las actualizaciones | **Aceptado con verificación en CI** |
| D4 | Dependencias de prueba (`pytest`, `httpx`) dentro del mismo `requirements.in` que runtime | Revisión manual | Se mantiene un solo archivo para que CI y Docker instalen lo mismo; separar runtime/test queda como mejora declarada | **Aceptado; mejora pendiente** |
| D5 | Sin SBOM | Revisión S13 | Se declara como trabajo futuro; `requirements.txt` con hashes y el lockfile de npm son el inventario actual | **Pendiente, aceptado** |
| D6 | SonarCloud marca instalaciones sin `--only-binary`/`--ignore-scripts` en los `Dockerfile` | Análisis estático (`docker:S8541`, `S8544`, `S6505`) | Corregido: `pip install --only-binary=:all: --require-hashes` en `Dockerfile` y `Dockploy/Dockerfile.api`; `npm ci --ignore-scripts` en ambos Dockerfile web | **Corregido en repositorio**; requiere push y nuevo análisis |
| D7 | SonarCloud marca lectura de rutas y peticiones en `scripts/medicion/bench_busqueda.py` (`S8703`, `S8707`) | Análisis estático | Se añadieron `_url_medible` (solo http/https y hosts locales salvo `SHAREU_BENCH_PERMITIR_REMOTO=1`) y `_destino_seguro` (nombre simple, extensión `.json`/`.md` y salida confinada a `docs/evidencia/mediciones`), con pruebas en `tests/test_bench_busqueda.py` | **Corregido en repositorio y validado en local**; el reanálisis llega con el push |
| D8 | SonarCloud marca `Depends`/`Header` en la firma de un endpoint (`python:S8410`) | Análisis estático | Se migraron las cabeceras de `administracion/router.py` y `documentos/router.py` a `Annotated` | **Corregido en repositorio**; requiere nuevo análisis |
| D9 | SonarCloud analiza `shareuwensite-main/`, el sitio estático legado (29 de 33 incidencias) | Análisis estático | No es el frontend canónico (ADR 0005). Se corrigieron sus 29 incidencias en el árbol (accesibilidad, ternarios y exports) en lugar de excluirlo; sigue siendo legado no desplegado | **Corregido en repositorio**; requiere push y nuevo análisis |

## 4. Reglas del equipo

1. Una dependencia nueva entra por `requirements.in`, se regenera `requirements.txt` con hashes y
   se justifica en el PR.
2. Un hallazgo de `pip-audit` **bloquea** el merge hasta corregirlo o documentar por qué no aplica
   (falso positivo, dependencia solo de desarrollo, sin ruta de explotación).
3. Un hallazgo de `npm audit` se revisa en el artefacto; si es `high` o `critical`, se abre un PR
   de Dependabot o se fija la versión.
4. No se versionan secretos ni `.env`; `.env.example` solo contiene marcadores.
5. Las imágenes Docker se construyen desde `requirements.txt` con hashes, no desde el entorno del
   desarrollador.

## 5. Resultado verificable

```text
$ .venv312\Scripts\python.exe -m pip_audit -r requirements.in
No known vulnerabilities found
```

El resultado local no sustituye al de CI: el pipeline es la fuente de verdad y su estado se
consulta en la pestaña *Actions*. Al 2026-11-21 los runs #44–#47 fallaron **sin jobs** porque el
workflow usaba `secrets` dentro de un `if` de paso, algo que GitHub rechaza al validar el archivo.
La corrección (token como `env` de job y condición sobre `env.SONAR_TOKEN`), junto con el paso
`scripts/validar_docs.py`, está en el árbol de trabajo y pendiente de push. Por eso este documento no
afirma que el pipeline esté en verde.

El **Quality Gate de SonarCloud está en ERROR** (`new_reliability_rating=3`,
`new_security_rating=3`, **33 incidencias abiertas**, consultado el 2026-11-21; 29 en el sitio
legado). Las 33 se corrigieron en el árbol. No se oculta: los hallazgos están clasificados en la
tabla D6–D9 y en [`../arc42/11-riesgos-y-deuda-tecnica.md`](../arc42/11-riesgos-y-deuda-tecnica.md)
§11.5.

## 6. Trazabilidad

[ADR 0014](../adr/0014-endurecimiento-http-y-escritura-autenticada.md) →
[`.github/workflows/tests.yml`](../../.github/workflows/tests.yml) →
[`.github/dependabot.yml`](../../.github/dependabot.yml) → `requirements.in` / `requirements.txt` →
este documento → [`amenazas.md`](amenazas.md) (T7) → `docs/evidencia/s13-amenazas.md`.
