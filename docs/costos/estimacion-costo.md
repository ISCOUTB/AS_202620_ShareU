# Estimación de costo mensual — ShareU

## 1. Restricción de partida

El proyecto se entrega bajo **USD 0/mes y sin tarjeta de crédito** (arc42 §2). La estimación no
justifica un gasto decidido: existe para saber **en qué punto** una capa gratuita deja de alcanzar y
qué habría que pagar. Las decisiones de plataforma están en ADR 0006 (backend) y ADR 0007
(frontend).

## 2. Supuesto de volumen

Volumen académico (demo de clase, sustentaciones y revisión del docente), no tráfico de producción:

| Variable | Supuesto |
|---|---|
| Usuarios simultáneos en una demo | 5–10 |
| Búsquedas por sustentación | ~50 |
| Búsquedas por día (pico de semana de entrega) | 1 000 |
| Publicaciones por día | 20 |
| Documentos en el catálogo al final del semestre | 200–1 000 |
| Despliegues | 1–3 por semana |
| Horas con tráfico real | < 5 h/mes |

## 3. Costo por pieza

| Pieza | Proveedor / plan | Costo | Qué cubre la capa gratuita | Dónde se rompe |
|---|---|---|---|---|
| **Backend y frontend** (contenedores `api` y `web`) | Servidor del laboratorio con **Dokploy** (Docker Compose) | **USD 0 para el equipo** (el servidor lo aporta el laboratorio) | CPU y memoria del servidor; los límites del compose son 0,5 CPU/256 MB y 0,5 CPU/192 MB | Si el laboratorio retira el servidor o se necesita más CPU/memoria; un VPS equivalente cuesta ≈ USD 5–10/mes y rompería el costo cero |
| **Base de datos** | **Firestore, plan Spark** (Firebase) | USD 0 | 1 GiB almacenado, **50 000 lecturas/día**, **20 000 escrituras/día**, 20 000 borrados/día, 10 GiB/mes de salida de red | Ver §4: la primera ruptura realista son las **lecturas/día** si se apaga la caché o el catálogo crece mucho |
| **Dominios** | `shareu.iscoutb.dev`, `api-shareu.iscoutb.dev` | USD 0 para el equipo | Subdominios del dominio institucional | Si el dominio deja de estar disponible o se necesita uno propio |
| **CI** | GitHub Actions, repositorio público | USD 0 | Minutos ilimitados en repos públicos | Si el repositorio pasa a privado (2 000 min/mes gratuitos) |
| **Calidad** | SonarCloud, proyecto público | USD 0 | Análisis ilimitado en repos públicos | Si el repositorio pasa a privado (SonarCloud gratuito exige público) |
| **Dependencias** | PyPI, npm, Dependabot | USD 0 | Uso normal | No aplica con el volumen actual |
| **Almacenamiento de archivos** | *No implementado* | USD 0 | — | Al implementarlo, un bucket gratuito (por ejemplo 5 GB) se rompe al superar ese tamaño o el tráfico |

## 4. Punto de ruptura de Firestore (el más probable)

Con la caché encendida, la medición S14 da **0,07 lecturas por búsqueda**. Con 1 000
búsquedas/día eso son **70 lecturas/día**, muy por debajo de las 50 000. El límite se alcanzaría
con ≈ **700 000 búsquedas/día** (o ≈ 50 000/día si la caché estuviera apagada y cada búsqueda
leyera la colección completa).

Las escrituras son más holgadas: 20 000/día con 20 publicaciones/día deja un margen de 1 000×.
El almacenamiento (1 GiB) admite del orden de **un millón de documentos** de ~1 KB; el catálogo del
semestre no se acerca.

**Primera ruptura realista:** no es el tráfico normal, sino una **prueba de carga** o un
`--sin-cache` prolongado. Si se acerca al límite, las opciones son: subir el TTL, añadir
*single-flight* (elimina el *stampede* de la caché fría), paginar o pasar a un plan de pago
(requiere tarjeta y reabre ADR 0012).

## 5. Punto de ruptura del despliegue

El servidor del laboratorio es el supuesto más frágil: no lo controla el equipo. Si deja de estar
disponible, el mismo `Dockploy/compose.lab.yml` se puede llevar a otro servidor con Docker, pero
dejaría de ser gratuito. Esa es la razón por la que el descriptor no depende de un proveedor
concreto y las URLs se declaran no verificadas mientras respondan 404.

## 6. Costo total

**USD 0/mes** con el volumen de §2, siempre que:

1. El repositorio siga público (CI y SonarCloud gratuitos).
2. El laboratorio mantenga el servidor y los subdominios.
3. El catálogo y el tráfico se mantengan dentro de la capa Spark.
4. No se incorporen archivos binarios ni un broker gestionado.

Si falla (1), el costo es el plan de GitHub/SonarCloud. Si falla (2), ≈ USD 5–10/mes de VPS. Si
falla (3), el plan de Firestore. Ninguna de esas condiciones se cumple hoy, y ninguna se oculta
como si el sistema fuera gratuito para siempre.

## 7. Trazabilidad

`docs/aspectos.md` (A8) → [ADR 0006](../adr/0006-plataforma-backend-despliegue.md),
[ADR 0007](../adr/0007-plataforma-frontend-despliegue.md),
[ADR 0012](../adr/0012-persistencia-en-firestore.md),
[ADR 0013](../adr/0013-cache-de-lectura-con-invalidacion.md) → este documento →
`docs/evidencia/mediciones/s14-local-asgi.md` (lecturas por búsqueda) → arc42 §7.4.
