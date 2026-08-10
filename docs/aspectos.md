# Idea del proyecto
EncuentraUTB es una plataforma web pensada para la comunidad de la Universidad Tecnológica de Bolívar. La idea principal es tener un espacio donde se puedan publicar objetos que hayan sido perdidos o encontrados dentro de la universidad. De esta manera, una persona que pierda algo puede buscarlo en la plataforma, mientras que quien encuentre un objeto puede registrarlo para ayudar a que llegue nuevamente a su dueño.
La plataforma permitiría buscar las publicaciones utilizando diferentes datos, como la categoría del objeto, el lugar donde fue perdido o encontrado, una palabra clave y la fecha. Esto haría que encontrar una publicación específica sea mucho más sencillo.

## Aspecto declarado: Usabilidad
La usabilidad es un aspecto crítico porque el valor principal de la plataforma depende de que las personas puedan buscar y filtrar publicaciones de forma ágil; si esto no es sencillo, los usuarios volverán a los métodos informales actuales (WhatsApp, voz a voz), que es precisamente el problema que el proyecto busca resolver.

### Escenario de calidad
 
| Elemento | Descripción |
|---|---|
| **Fuente del estímulo** | Un usuario de la comunidad UTB (estudiante, docente, administrativo o visitante) |
| **Estímulo** | El usuario ingresa a la plataforma buscando un objeto perdido o encontrado específico |
| **Artefacto** | Módulo de búsqueda y filtrado de publicaciones |
| **Entorno** | Uso normal, desde computador o celular, con o sin experiencia previa en la plataforma |
| **Respuesta** | El sistema permite filtrar resultados por categoría, lugar, fecha y/o palabra clave, mostrando publicaciones relevantes de forma clara |
| **Medida de respuesta** | El usuario logra encontrar (o descartar) una publicación relevante en menos de 3 interacciones (clics/filtros), sin necesidad de ayuda externa o instrucciones adicionales |
 
### Decisiones/tácticas para lograrlo
 
- Interfaz de filtros simple y visible (categoría, lugar, fecha, palabra clave) en la misma vista de resultados, evitando pasos adicionales.
- Uso de componentes de UI estándar y reconocibles (buscador con ícono de lupa, menús desplegables, chips de filtro) para reducir la curva de aprendizaje.
- Resultados de búsqueda con información clave visible de inmediato (foto, categoría, lugar, fecha) sin tener que abrir cada publicación.
- Diseño responsivo, priorizando el uso desde celular, dado que es el dispositivo más común entre estudiantes.
- Mensajes claros cuando no hay resultados, sugiriendo ajustar los filtros en lugar de dejar una pantalla vacía sin explicación.
### Forma de verificación
 
- Pruebas de usabilidad con un grupo reducido de usuarios reales (estudiantes/docentes), midiendo tiempo y número de clics para encontrar una publicación de prueba.
- Revisión heurística de la interfaz de búsqueda y filtros antes de cada entrega incremental.
 
