# ADR 0004: Integración síncrona y asíncrona en ShareU

* **Estado:** Propuesto
* **Fecha:** septiembre de 2026

## Contexto

ShareU es una plataforma web para compartir y encontrar material académico organizado por universidad, carrera y materia. La arquitectura adoptada para el sistema es un monolito modular, donde los módulos mantienen responsabilidades de dominio claramente separadas y los accesos entre módulos se realizan mediante interfaces de servicio.

Durante la definición de las integraciones del backend se identifican dos tipos de comunicación con componentes externos o de infraestructura:

* **Backend → almacenamiento:** utilizada para persistir información necesaria para completar operaciones del sistema, como documentos y sus metadatos.
* **Backend → correo:** utilizada para enviar notificaciones que no forman parte del resultado principal de la operación solicitada por el usuario.

La decisión debe considerar principalmente el **acoplamiento temporal** y los **modos de fallo** de cada integración.

El acoplamiento temporal determina si el componente que realiza una solicitud debe esperar una respuesta para poder continuar. Cuando existe un acoplamiento temporal fuerte, una comunicación síncrona permite confirmar el resultado antes de continuar. Cuando la respuesta no es necesaria para completar inmediatamente la operación principal, una comunicación asíncrona permite desacoplar ambos procesos.

## Decisión

Se establece que la integración entre **backend y almacenamiento será síncrona**, mientras que la integración entre **backend y servicio de correo será asíncrona**.

### Backend → almacenamiento: síncrona

La comunicación con el almacenamiento será síncrona porque el backend necesita conocer el resultado de la operación de persistencia antes de confirmar al usuario que la operación principal se completó correctamente.

Existe un **acoplamiento temporal fuerte**: el backend debe esperar la confirmación del almacenamiento para determinar si la información fue guardada correctamente.

Por ejemplo, cuando un usuario carga un documento, el flujo esperado es:

1. El usuario solicita la carga del documento.
2. El backend valida la solicitud.
3. El backend envía la información al almacenamiento.
4. El almacenamiento confirma o rechaza la operación.
5. El backend registra el resultado y responde al usuario.

Esta decisión permite evitar que el backend informe una operación como exitosa cuando el almacenamiento realmente falló.

### Modos de fallo del almacenamiento

Entre los principales modos de fallo se consideran:

* El almacenamiento no está disponible.
* Se produce un error durante la escritura.
* Se presenta un problema de conexión.
* Se produce un timeout.
* La información no puede persistirse correctamente.

En estos casos, la comunicación síncrona permite que el backend detecte el fallo y entregue una respuesta coherente al usuario. La operación puede ser rechazada o marcada como fallida en lugar de aparentar una persistencia exitosa.

Por lo tanto, aunque la comunicación síncrona genera una dependencia temporal entre el backend y el almacenamiento, esta dependencia es necesaria porque la confirmación de persistencia forma parte del resultado de la operación principal.

### Backend → correo: asíncrona

La comunicación con el servicio de correo será asíncrona porque el envío de una notificación no debe bloquear la operación principal del sistema.

Existe un **acoplamiento temporal débil**: una vez que el backend ha completado la operación principal, el envío del correo puede ejecutarse de manera independiente.

Por ejemplo, si ShareU necesita enviar una notificación después de una operación:

1. El usuario realiza una operación.
2. El backend procesa y confirma la operación principal.
3. El backend genera una solicitud de envío de correo.
4. El servicio de correo procesa la solicitud de forma independiente.
5. Si es necesario, el envío puede reintentarse.

De esta manera, el usuario no necesita esperar la respuesta del proveedor de correo para recibir la confirmación de una operación que ya fue completada correctamente.

### Modos de fallo del correo

Entre los principales modos de fallo se consideran:

* El servicio de correo no está disponible.
* Se produce un timeout.
* Existe una interrupción temporal de red.
* El proveedor rechaza temporalmente la solicitud.
* Se alcanza un límite de solicitudes.
* El envío falla después de que la operación principal ya fue completada.

Al utilizar una integración asíncrona, estos fallos no tienen que impedir necesariamente que la operación principal de ShareU termine correctamente.

El mensaje puede permanecer pendiente para ser procesado posteriormente o ser reintentado según el mecanismo de mensajería que se implemente.

La consecuencia es que existe una posible demora entre la operación principal y la recepción del correo, pero se reduce el acoplamiento temporal y se evita que la disponibilidad del servicio de correo bloquee funcionalidades principales de ShareU.

## Alternativas consideradas

### Backend → almacenamiento asíncrono — descartada

**Ventaja:**

* Reduce el acoplamiento temporal entre el backend y el almacenamiento.
* El backend podría continuar procesando la solicitud sin esperar inmediatamente la confirmación del almacenamiento.

**Desventaja:**

* El backend no tendría confirmación inmediata de que la información fue almacenada correctamente.
* Un fallo del almacenamiento podría producir una diferencia entre el resultado informado al usuario y el estado real de los datos.
* Requiere mecanismos adicionales para gestionar reintentos, estados pendientes y consistencia.

**Consecuencia:**

Se descarta para esta integración porque la persistencia forma parte del resultado de operaciones principales como la carga y actualización de información. Se prioriza conocer el resultado del almacenamiento antes de confirmar la operación al usuario.

### Backend → almacenamiento síncrono — seleccionada

**Ventaja:**

* Permite conocer inmediatamente si la operación de persistencia fue exitosa.
* Facilita mantener una respuesta coherente entre el backend y el estado real del almacenamiento.
* Simplifica el manejo inicial de errores.

**Desventaja:**

* El backend queda temporalmente dependiente de la disponibilidad del almacenamiento.
* Un timeout o indisponibilidad del almacenamiento puede aumentar el tiempo de respuesta de la operación.

**Consecuencia:**

Se acepta este acoplamiento temporal porque la confirmación de persistencia es necesaria para completar correctamente determinadas operaciones del sistema.

### Backend → correo síncrono — descartada

**Ventaja:**

* El backend puede conocer inmediatamente si el proveedor aceptó la solicitud de envío.
* El flujo es sencillo de implementar inicialmente.

**Desventaja:**

* El tiempo de respuesta del servicio de correo afecta directamente al tiempo de respuesta del backend.
* Una caída o lentitud del proveedor puede bloquear o retrasar una operación que no depende funcionalmente del envío inmediato del correo.
* Aumenta el acoplamiento temporal con un servicio externo.

**Consecuencia:**

Se descarta porque el envío de correo no debe impedir que las operaciones principales de ShareU finalicen cuando el servicio de correo presenta problemas.

### Backend → correo asíncrono — seleccionada

**Ventaja:**

* Reduce el acoplamiento temporal entre el backend y el servicio de correo.
* Permite que la operación principal finalice sin esperar el envío.
* Facilita implementar reintentos ante fallos temporales.
* Evita que la disponibilidad del proveedor de correo afecte directamente las operaciones principales.

**Desventaja:**

* El correo puede recibirse después de que la operación principal haya terminado.
* Requiere gestionar estados pendientes, errores y posibles reintentos.
* La confirmación del envío no está disponible inmediatamente dentro de la misma solicitud.

**Consecuencia:**

Se acepta el procesamiento asíncrono porque la notificación por correo es una actividad secundaria respecto a la operación principal y puede ejecutarse independientemente.

## Consecuencias

### Positivas

* Las operaciones que requieren persistencia reciben una confirmación clara del almacenamiento.
* Se evita que un fallo del correo bloquee innecesariamente las operaciones principales.
* Se reduce el acoplamiento temporal con servicios externos que no son críticos para completar la operación.
* Los fallos del servicio de correo pueden gestionarse mediante reintentos.
* Se mantiene una separación clara entre operaciones críticas y tareas secundarias.

### Negativas

* El almacenamiento puede aumentar el tiempo de respuesta cuando presenta latencia o indisponibilidad.
* El envío asíncrono de correo introduce complejidad adicional para gestionar pendientes y reintentos.
* Puede existir una demora entre la finalización de una operación y la recepción de su notificación por correo.
* El sistema debe definir mecanismos para evitar pérdida de mensajes cuando sea necesario garantizar la entrega.

## Reglas de implementación

1. Las operaciones que requieran confirmación de persistencia utilizarán comunicación síncrona con el almacenamiento.
2. Las notificaciones por correo no deben bloquear la finalización de la operación principal.
3. Los fallos del almacenamiento deben comunicarse como resultado de la operación cuando impidan completar la persistencia.
4. Los fallos temporales del servicio de correo deberán poder gestionarse mediante reintentos.
5. La implementación asíncrona deberá contemplar el manejo de mensajes pendientes y errores.
6. Cualquier cambio de esta decisión deberá documentarse mediante una revisión de este ADR o mediante un nuevo ADR cuando la arquitectura evolucione.

## Criterio de reapertura

Esta decisión podrá revisarse si:

* El almacenamiento deja de requerir confirmación inmediata para las operaciones principales.
* El sistema incorpora un mecanismo de persistencia eventual que garantice la consistencia requerida.
* El servicio de correo pasa a ser parte crítica del resultado de una operación.
* Aparecen nuevos requisitos de disponibilidad, rendimiento o consistencia que cambien las necesidades actuales.

## Referencias

* [`docs/adr/0001-estilo-arquitectonico.md`](0001-estilo-arquitectonico.md)
* [`docs/aspectos/aspectos.md`](../aspectos/aspectos.md)
* [`docs/arc42/arc42.md`](../arc42/arc42.md)
