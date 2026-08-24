---
date: agosto 2026
title: "![arc42](images/arc42-logo.png) Template"
---

# 

# Introduction and Goals {#section-introduction-and-goals}
Actualmente, los estudiantes universitarios utilizan diferentes medios para compartir y conseguir material académico, como apuntes, talleres, ejercicios, parciales y documentos de estudio. Sin embargo, este material suele encontrarse disperso en grupos de WhatsApp, redes sociales, servicios de almacenamiento o conversaciones entre compañeros, lo que dificulta encontrar información específica cuando se necesita.

A partir de esta problemática surge ShareU, una plataforma web orientada a estudiantes universitarios que busca centralizar y organizar el material académico en un solo lugar. La plataforma permitirá a los usuarios compartir documentos, buscar material de diferentes materias, descargar recursos y calificarlos según su utilidad. Además, los documentos podrán organizarse por universidad, carrera y materia, facilitando su localización.

El propósito principal de ShareU es simplificar el acceso y el intercambio de recursos académicos, reduciendo el tiempo que los estudiantes deben dedicar a buscar material en diferentes plataformas. Para esto, se plantea una interfaz sencilla y herramientas de búsqueda y filtrado que permitan encontrar documentos de manera rápida y organizada.

## Requirements Overview {#_requirements_overview}

ShareU es una plataforma web orientada a estudiantes universitarios que tiene como propósito facilitar el intercambio y acceso a material académico. El sistema debe permitir que los estudiantes compartan documentos y que otros usuarios puedan encontrarlos de manera sencilla, utilizando diferentes criterios de búsqueda y clasificación.

Los principales requisitos de ShareU están relacionados con la gestión de usuarios, documentos y búsqueda de material académico. Los usuarios deberán poder registrarse e iniciar sesión, crear y administrar su perfil, subir documentos y clasificarlos según la universidad, carrera y materia. También podrán buscar documentos, consultar su información, descargarlos y calificarlos según su utilidad.

Además, la plataforma contará con un mecanismo para reportar documentos que puedan contener información incorrecta, contenido inapropiado o que incumplan las reglas de la plataforma. Estos reportes serán gestionados por un administrador, quien tendrá permisos para revisar y administrar usuarios y documentos.

Entre los requisitos principales del sistema se encuentran:

* **Gestión de usuarios:** registro, inicio de sesión y administración del perfil.
* **Gestión de documentos:** subida, clasificación, consulta y descarga de material académico.
* **Búsqueda y filtrado:** búsqueda mediante palabras clave y filtros como universidad, carrera, materia y tipo de documento.
* **Calificación:** los usuarios podrán valorar los documentos para ayudar a identificar el material más útil.
* **Administración:** el administrador podrá gestionar usuarios, documentos y reportes.
* **Usabilidad:** la plataforma deberá ofrecer una interfaz sencilla e intuitiva que permita encontrar y compartir material sin procesos innecesariamente complejos.
* **Seguridad:** el sistema deberá proteger las cuentas de los usuarios y controlar el acceso a las funcionalidades según el tipo de usuario.

El requisito de calidad más importante para ShareU es la **usabilidad**, debido a que la utilidad de la plataforma depende de que los estudiantes puedan encontrar el material que necesitan de forma rápida y sencilla. También se consideran importantes la seguridad, el rendimiento, la disponibilidad y la mantenibilidad del sistema.


## Quality Goals {#_quality_goals}

Los objetivos de calidad de ShareU están orientados a garantizar que la plataforma sea fácil de utilizar, segura, rápida y confiable para los estudiantes. Estos objetivos permiten establecer criterios que servirán para evaluar si el sistema cumple con las características esperadas durante su desarrollo.

Los principales objetivos de calidad son:

| **Objetivo de calidad** | **Descripción**                                                                                                                                            | **Prioridad** |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **Usabilidad**          | La plataforma debe ser sencilla e intuitiva, permitiendo que los estudiantes encuentren, suban y descarguen material académico sin dificultad.             | **Muy alta**  |
| **Seguridad**           | La información de los usuarios y sus documentos debe estar protegida, evitando accesos no autorizados y controlando los permisos según el tipo de usuario. | **Alta**      |
| **Rendimiento**         | Las búsquedas, consultas y acciones principales deben ejecutarse rápidamente para evitar esperas innecesarias.                                             | **Alta**      |
| **Disponibilidad**      | La plataforma debe estar disponible para que los estudiantes puedan consultar y compartir material cuando lo necesiten.                                    | **Alta**      |
| **Mantenibilidad**      | El sistema debe estar organizado de manera que sea posible corregir errores, realizar cambios y agregar nuevas funcionalidades sin afectar las existentes. | **Media**     |
| **Escalabilidad**       | La plataforma debe poder soportar un aumento progresivo de usuarios y documentos sin afectar significativamente su funcionamiento.                         | **Media**     |

### Priorización

La **usabilidad** es el principal objetivo de calidad de ShareU, ya que la plataforma busca facilitar el acceso al material académico y reducir el tiempo que los estudiantes dedican a encontrarlo. Una interfaz complicada o un proceso de búsqueda poco claro disminuiría considerablemente la utilidad del sistema.

La **seguridad** también tiene una prioridad muy alta debido a que ShareU manejará cuentas de usuarios, documentos y diferentes niveles de permisos. Por otro lado, el **rendimiento y la disponibilidad** son importantes para garantizar una experiencia fluida durante la búsqueda y descarga de material.

Finalmente, la **mantenibilidad y escalabilidad** permitirán que ShareU pueda evolucionar con el tiempo, incorporando nuevas funcionalidades y soportando un mayor número de usuarios y documentos.


## Stakeholders {#_stakeholders}

+-------------+---------------------------+---------------------------+
| Role/Name   | Contact                   | Expectations              |
+=============+===========================+===========================+
|             | *\<Contact-1\>*           | *\<Expectation-1\>*       |
|*\<Role-1\>* |                           |                           |
+-------------+---------------------------+---------------------------+
|*\<Role-2\>* | *\<Contact-2\>*           | *\<Expectation-2\>*       |
+-------------+---------------------------+---------------------------+

# Architecture Constraints {#section-architecture-constraints}

# Context and Scope {#section-context-and-scope}

## Business Context {#_business_context}

**\<Diagram or Table\>**

**\<optionally: Explanation of external domain interfaces\>**

## Technical Context {#_technical_context}

**\<Diagram or Table\>**

**\<optionally: Explanation of technical interfaces\>**

**\<Mapping Input/Output to Channels\>**

# Solution Strategy {#section-solution-strategy}

## Decisión de estilo arquitectónico

Se evaluaron tres estilos sobre el mismo escenario prioritario de ShareU —
usabilidad en la búsqueda y filtrado de documentos (`docs/aspectos.md`)— y
sobre los objetivos de calidad definidos arriba.

| | Capas | Hexagonal | Monolito modular |
|---|---|---|---|
| **Frontera** | Capa técnica (presentación / lógica / datos) | Puertos y adaptadores | Módulo de dominio |
| **Atributo que favorece** | Simplicidad inicial | Testabilidad y sustitución de infraestructura | Evolución gradual por dominio |
| **Costo que introduce** | Cambios transversales al crecer el dominio | Más indirección, curva de aprendizaje | Disciplina de límites entre módulos |
| **Se rompe cuando** | El dominio crece más que la capa | El equipo no sostiene la abstracción | Nadie vigila el acoplamiento |
| **Ajuste a ShareU** | Bajo: la búsqueda, la calificación y la moderación son dominios distintos que compartirían capa de servicio | Medio: buena testabilidad, pero el equipo no tiene experiencia previa ni tiempo para sostenerla esta fase | Alto: los dominios de ShareU (usuarios, documentos, búsqueda, calificaciones, administración) mapean directo a módulos |

**Decisión:** monolito modular. Ver justificación completa, alternativas
descartadas y consecuencias en `docs/adr/0001-estilo-arquitectonico.md`.

## Estructura de módulos resultante

- `usuarios` — registro, autenticación, perfil.
- `documentos` — subida, clasificación (universidad/carrera/materia), descarga.
- `busqueda` — filtrado y ranking de resultados (módulo crítico para el
  escenario de usabilidad priorizado).
- `calificaciones` — valoración de documentos.
- `administracion` — reportes, moderación, gestión de usuarios y documentos.

Cada módulo expone su propia interfaz interna; ningún módulo accede a los
datos internos de otro directamente. Ver `app/` para el esqueleto ejecutable
con esta estructura.

## Tácticas por atributo de calidad

Ver tabla de tácticas seleccionadas en `docs/adr/0001-estilo-arquitectonico.md`
(sección "Tácticas seleccionadas para los atributos priorizados"): usabilidad
(filtros visibles, resultados con info clave), seguridad (control de acceso
por rol), rendimiento (índice y caché en búsqueda) y modificabilidad
(SOLID/GRASP dentro de cada módulo).

## Principios y patrones de nivel de código y módulo

- **Nivel código:** SOLID y GRASP como criterio de asignación de
  responsabilidades dentro de cada módulo, no como catecismo.
- **Nivel módulo:** patrones de diseño (Factory, Strategy, Observer, etc.) se
  aplican donde resuelvan un problema puntual de un módulo; no sustituyen la
  decisión de estilo del ADR 0001.

## Trazabilidad

Esta estrategia de solución está motivada por el escenario de calidad de
usabilidad declarado en `docs/aspectos.md` y queda registrada formalmente en
`docs/adr/0001-estilo-arquitectonico.md`.

# Building Block View {#section-building-block-view}

## Whitebox Overall System {#_whitebox_overall_system}

***\<Overview Diagram\>***

Motivation

:   *\<text explanation\>*

Contained Building Blocks

:   *\<Description of contained building block (black boxes)\>*

Important Interfaces

:   *\<Description of important interfaces\>*

### \<Name black box 1\> {#_name_black_box_1}

*\<Purpose/Responsibility\>*

*\<Interface(s)\>*

*\<(Optional) Quality/Performance Characteristics\>*

*\<(Optional) Directory/File Location\>*

*\<(Optional) Fulfilled Requirements\>*

*\<(optional) Open Issues/Problems/Risks\>*

### \<Name black box 2\> {#_name_black_box_2}

*\<black box template\>*

### \<Name black box n\> {#_name_black_box_n}

*\<black box template\>*

### \<Name interface 1\> {#_name_interface_1}

...​

### \<Name interface m\> {#_name_interface_m}

## Level 2 {#_level_2}

### White Box *\<building block 1\>* {#_white_box_building_block_1}

*\<white box template\>*

### White Box *\<building block 2\>* {#_white_box_building_block_2}

*\<white box template\>*

...​

### White Box *\<building block m\>* {#_white_box_building_block_m}

*\<white box template\>*

## Level 3 {#_level_3}

### White Box \<\_building block x.1\_\> {#_white_box_building_block_x_1}

*\<white box template\>*

### White Box \<\_building block x.2\_\> {#_white_box_building_block_x_2}

*\<white box template\>*

### White Box \<\_building block y.1\_\> {#_white_box_building_block_y_1}

*\<white box template\>*

# Runtime View {#section-runtime-view}

## \<Runtime Scenario 1\> {#_runtime_scenario_1}

-   *\<insert runtime diagram or textual description of the scenario\>*

-   *\<insert description of the notable aspects of the interactions
    between the building block instances depicted in this diagram.\>*

## \<Runtime Scenario 2\> {#_runtime_scenario_2}

## ...​

## \<Runtime Scenario n\> {#_runtime_scenario_n}

# Deployment View {#section-deployment-view}

## Infrastructure Level 1 {#_infrastructure_level_1}

***\<Overview Diagram\>***

Motivation

:   *\<explanation in text form\>*

Quality and/or Performance Features

:   *\<explanation in text form\>*

Mapping of Building Blocks to Infrastructure

:   *\<description of the mapping\>*

## Infrastructure Level 2 {#_infrastructure_level_2}

### *\<Infrastructure Element 1\>* {#_infrastructure_element_1}

*\<diagram + explanation\>*

### *\<Infrastructure Element 2\>* {#_infrastructure_element_2}

*\<diagram + explanation\>*

...​

### *\<Infrastructure Element n\>* {#_infrastructure_element_n}

*\<diagram + explanation\>*

# Cross-cutting Concepts {#section-concepts}

## *\<Concept 1\>* {#_concept_1}

*\<explanation\>*

## *\<Concept 2\>* {#_concept_2}

*\<explanation\>*

...​

## *\<Concept n\>* {#_concept_n}

*\<explanation\>*

# Architecture Decisions {#section-design-decisions}

Ver `docs/adr/`. Registrado hasta ahora:

* [ADR 0001 — Estilo arquitectónico de ShareU](adr/0001-estilo-arquitectonico.md): monolito modular.

# Quality Requirements {#section-quality-scenarios}
.
## Quality Requirements Overview {#_quality_requirements_overview}
.
## Quality Scenarios {#_quality_scenarios}

Ver el escenario de usabilidad detallado en `docs/aspectos.md`.

# Risks and Technical Debts {#section-technical-risks}

* El monolito modular (ADR 0001) requiere disciplina de equipo para no acoplar módulos; sin revisión periódica, la frontera entre dominios puede erosionarse.

# Glossary {#section-glossary}

+----------------------+-----------------------------------------------+
| Term                 | Definition                                    |
+======================+===============================================+
| *\<Term-1\>*         | *\<definition-1\>*                            |
+----------------------+-----------------------------------------------+
| *\<Term-2\>*         | *\<definition-2\>*                            |
+----------------------+-----------------------------------------------+
