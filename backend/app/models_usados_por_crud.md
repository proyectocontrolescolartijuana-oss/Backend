# Modelos usados por CRUD

Este documento resume los modelos de SQLAlchemy que usa cada archivo dentro de `backend/app/crud`.

## Resumen por archivo CRUD

| Archivo CRUD | Modelo principal usado | Archivo del modelo | Tabla SQL | Uso dentro del CRUD |
| --- | --- | --- | --- | --- |
| `crud_alumno.py` | `Alumno` | `app/models/alumno.py` | `alumnos` | Listar, obtener por id, crear, actualizar y eliminar alumnos. |
| `crud_alumno_tutor.py` | `alumno_tutor` | `app/models/alumno_tutor.py` | `alumno_tutor` | Crear, consultar y eliminar relaciones entre alumnos y tutores. |
| `crud_asistencia.py` | `Asistencia` | `app/models/asistencia.py` | `asistencias` | Listar, obtener por id, crear, actualizar y eliminar asistencias. |
| `crud_calificacion.py` | `Calificacion` | `app/models/calificacion.py` | `calificaciones` | Listar, obtener por id, crear, actualizar y eliminar calificaciones. |
| `crud_carrera.py` | `Carrera` | `app/models/carrera.py` | `carreras` | Listar, obtener por id, crear, actualizar y eliminar carreras. |
| `crud_carga_academica.py` | `CargaAcademica` | `app/models/carga_academica.py` | `carga_academica` | Listar, obtener por id, crear, actualizar y eliminar cargas academicas. |
| `crud_contacto_emergencia.py` | `ContactoEmergencia` | `app/models/contacto_emergencia.py` | `contactos_emergencia` | Listar, obtener por id, crear, actualizar y eliminar contactos de emergencia. |
| `crud_cuatrimestre.py` | `Cuatrimestre` | `app/models/cuatrimestre.py` | `cuatrimestres` | Listar, obtener por id, crear, actualizar y eliminar cuatrimestres. |
| `crud_docente.py` | `Docente` | `app/models/docente.py` | `docentes` | Listar, obtener por id, crear, actualizar y eliminar docentes. |
| `crud_documento_alumno.py` | `DocumentoAlumno` | `app/models/documento_alumno.py` | `documentos_alumno` | Listar, obtener por id, crear, actualizar y eliminar documentos de alumno. |
| `crud_empresa.py` | `Empresa` | `app/models/empresa.py` | `empresas` | Listar, obtener por id, crear, actualizar y eliminar empresas. |
| `crud_extraordinario.py` | `Extraordinario` | `app/models/extraordinario.py` | `extraordinarios` | Listar, obtener por id, crear, actualizar y eliminar extraordinarios. |
| `crud_grupo.py` | `Grupo` | `app/models/grupo.py` | `grupos` | Listar, obtener por id, crear, actualizar y eliminar grupos. |
| `crud_grupo_materia.py` | `GrupoMateria` | `app/models/grupo_materia.py` | `grupos_materias` | Listar, obtener por id, crear, actualizar y eliminar relaciones grupo-materia. |
| `crud_historial_academico.py` | `HistorialAcademico` | `app/models/historial_academico.py` | `historial_academico` | Listar, obtener por id, crear, actualizar y eliminar historial academico. |
| `crud_inscripcion.py` | `Inscripcion` | `app/models/inscripcion.py` | `inscripciones` | Listar, obtener por id, crear, actualizar y eliminar inscripciones. |
| `crud_materia.py` | `Materia` | `app/models/materia.py` | `materias` | Listar, obtener por id, crear, actualizar y eliminar materias. |
| `crud_parcial.py` | `Parcial` | `app/models/parcial.py` | `parciales` | Listar, obtener por id, crear, actualizar y eliminar parciales. |
| `crud_periodo.py` | `Periodo` | `app/models/periodo.py` | `periodos` | Listar, obtener por id, crear, actualizar y eliminar periodos. |
| `crud_plan_estudio.py` | `PlanEstudio`, `PlanMateria` | `app/models/plan_estudio.py`, `app/models/plan_materia.py` | `planes_estudio`, `plan_materias` | Crear planes de estudio, asociar materias al plan, consultar planes con relaciones, actualizar y eliminar. |
| `crud_practica_profesional.py` | `PracticaProfesional` | `app/models/practica_profesional.py` | `practicas_profesionales` | Listar, obtener por id, crear, actualizar y eliminar practicas profesionales. |
| `crud_procedencia_academica.py` | `ProcedenciaAcademica` | `app/models/procedencia_academica.py` | `procedencia_academica` | Listar, obtener por id, crear, actualizar y eliminar procedencias academicas. |
| `crud_recepcion_documento.py` | `RecepcionDocumento` | `app/models/recepcion_documento.py` | `recepcion_documentos` | Listar, obtener por id, crear, actualizar y eliminar recepciones de documentos. |
| `crud_rol.py` | `Rol` | `app/models/rol.py` | `roles` | Listar, obtener por id, crear, actualizar y eliminar roles. |
| `crud_seguro_medico.py` | `SeguroMedico` | `app/models/seguro_medico.py` | `seguros_medicos` | Listar, obtener por id, crear, actualizar y eliminar seguros medicos. |
| `crud_servicio_social.py` | `ServicioSocial` | `app/models/servicio_social.py` | `servicio_social` | Listar, obtener por id, crear, actualizar y eliminar servicios sociales. |
| `crud_tipo_documento.py` | `TipoDocumento` | `app/models/tipo_documento.py` | `tipos_documento` | Listar, obtener por id, crear, actualizar y eliminar tipos de documento. |
| `crud_titulacion.py` | `Titulacion` | `app/models/titulacion.py` | `titulacion` | Listar, obtener por id, crear, actualizar y eliminar titulaciones. |
| `crud_tutor.py` | `Tutor` | `app/models/tutor.py` | `tutores` | Listar, obtener por id, crear, actualizar y eliminar tutores. |
| `crud_usuario.py` | `Usuario` | `app/models/usuario.py` | `usuarios` | Listar, obtener por id, crear usuarios con password hasheada, actualizar y eliminar usuarios. |
| `crud_usuario_rol.py` | `usuario_roles` | `app/models/usuario_rol.py` | `usuario_roles` | Crear, consultar y eliminar relaciones entre usuarios y roles. |

## Relaciones relevantes usadas o expuestas

### `crud_plan_estudio.py`

Este es el CRUD con mas relaciones cargadas explicitamente.

- Usa directamente `PlanEstudio` para crear, consultar, actualizar y eliminar planes.
- Usa directamente `PlanMateria` para agregar materias a un plan en `crear_plan_estudio`.
- En `obtener_planes` carga relaciones con `joinedload`:
  - `PlanEstudio.carrera`, relacionada con el modelo `Carrera`.
  - `PlanEstudio.materias`, relacionada con el modelo `PlanMateria`.
  - `PlanMateria.materia`, relacionada con el modelo `Materia`.
  - `PlanMateria.cuatrimestre`, relacionada con el modelo `Cuatrimestre`.
- En `transformar_plan` se leen datos de:
  - `plan.carrera`
  - `plan.materias`
  - `pm.materia`
  - `pm.cuatrimestre`

Aunque `Carrera`, `Materia` y `Cuatrimestre` no se importan directamente en `crud_plan_estudio.py`, el CRUD depende de esas relaciones definidas en los modelos.

### `crud_alumno.py`

Usa directamente `Alumno`. El modelo `Alumno` tiene relaciones con:

- `Usuario`
- `Carrera`
- `PlanEstudio`
- `ContactoEmergencia`
- `SeguroMedico`
- `ProcedenciaAcademica`

El CRUD no usa `joinedload` ni consulta esas relaciones de forma explicita, pero pueden aparecer al serializar respuestas si los schemas las incluyen.

### `crud_calificacion.py`

Usa directamente `Calificacion`. El modelo `Calificacion` tiene relaciones con:

- `CargaAcademica`
- `Parcial`
- `Usuario`

El CRUD solo consulta `Calificacion` directamente.

### `crud_titulacion.py`

Usa directamente `Titulacion`. El modelo `Titulacion` tiene relacion con:

- `Alumno`

El CRUD solo consulta `Titulacion` directamente.

## CRUD disponibles en routers

Los routers importan estos CRUD:

| Router | CRUD usado |
| --- | --- |
| `alumnos.py` | `crud_alumno.py` |
| `calificaciones.py` | `crud_calificacion.py` |
| `carreras.py` | `crud_carrera.py` |
| `docentes.py` | `crud_docente.py` |
| `documentos.py` | `crud_alumno.py` (`get_alumno`) |
| `materias.py` | `crud_materia.py` |
| `parciales.py` | `crud_parcial.py` |
| `periodos.py` | `crud_periodo.py` |
| `plan_estudio.py` | `crud_plan_estudio.py` |
| `titulaciones.py` | `crud_titulacion.py` |
| `usuarios.py` | `crud_usuario.py` |

En `routers/roles.py` las importaciones de `crud_rol.py` aparecen comentadas, por lo que actualmente el router de roles no esta usando ese CRUD de forma activa.

## Modelos sin CRUD directo encontrado

Despues de agregar los CRUD faltantes, no quedan modelos de `backend/app/models` sin archivo CRUD directo, considerando tambien las tablas pivote `alumno_tutor` y `usuario_roles`.

Nota: `PlanMateria` no tiene un archivo CRUD independiente porque ya se maneja directamente dentro de `crud_plan_estudio.py`.

## Mejoras propuestas para los GET nuevos

Actualmente los routers nuevos devuelven principalmente los campos directos de cada tabla. Eso funciona para CRUD basico, pero en pantallas reales obliga al frontend a hacer muchas peticiones extra para resolver nombres de alumno, materia, docente, grupo o empresa. Estas son mejoras recomendadas.

### `GET /asistencias`

Mejora recomendada: devolver la asistencia con informacion de alumno, materia, grupo y periodo.

Relaciones a cargar:

- `Asistencia.carga`
- `CargaAcademica.alumno`
- `Alumno.usuario`
- `CargaAcademica.grupo_materia`
- `GrupoMateria.materia`
- `GrupoMateria.grupo`
- `GrupoMateria.periodo`

Respuesta sugerida:

```json
{
  "id_asistencia": 1,
  "fecha": "2026-01-12",
  "asistencia": true,
  "alumno": {
    "id_alumno": 1,
    "matricula": "20260001",
    "nombre": "Juan Perez Gomez"
  },
  "materia": {
    "id_materia": 6,
    "nombre": "Bases Biologicas del Comportamiento"
  },
  "grupo": {
    "id_grupo": 1,
    "nombre": "CRIM27"
  },
  "periodo": {
    "id_periodo": 1,
    "nombre": "Enero - Abril 2026"
  }
}
```

Filtros utiles:

- `GET /asistencias?alumno_id=1`
- `GET /asistencias?grupo_id=1`
- `GET /asistencias?materia_id=6`
- `GET /asistencias?periodo_id=1`
- `GET /asistencias?fecha_inicio=2026-01-01&fecha_fin=2026-01-31`

### `GET /cargas-academicas`

Mejora recomendada: devolver la carga con alumno, materia, docente, grupo y periodo. Este endpoint puede servir como base para horarios, listas de alumnos por materia y captura de calificaciones/asistencias.

Relaciones a cargar:

- `CargaAcademica.alumno`
- `Alumno.usuario`
- `CargaAcademica.grupo_materia`
- `GrupoMateria.materia`
- `GrupoMateria.docente`
- `Docente.usuario`
- `GrupoMateria.grupo`
- `GrupoMateria.periodo`

Filtros utiles:

- `GET /cargas-academicas?alumno_id=1`
- `GET /cargas-academicas?grupo_id=1`
- `GET /cargas-academicas?docente_id=1`
- `GET /cargas-academicas?materia_id=6`
- `GET /cargas-academicas?periodo_id=1`
- `GET /cargas-academicas?estatus=CURSANDO`

### `GET /grupos-materias`

Mejora recomendada: devolver la relacion grupo-materia con nombres legibles de grupo, materia, docente y periodo.

Relaciones a cargar:

- `GrupoMateria.grupo`
- `GrupoMateria.materia`
- `GrupoMateria.docente`
- `Docente.usuario`
- `GrupoMateria.periodo`

Respuesta sugerida:

```json
{
  "id_grupo_materia": 1,
  "aula": "A-101",
  "cupo_maximo": 40,
  "grupo": "CRIM27",
  "materia": "Bases Biologicas del Comportamiento",
  "docente": "Carlos Ramirez Lopez",
  "periodo": "Enero - Abril 2026"
}
```

Filtros utiles:

- `GET /grupos-materias?grupo_id=1`
- `GET /grupos-materias?docente_id=1`
- `GET /grupos-materias?periodo_id=1`
- `GET /grupos-materias?materia_id=6`

### `GET /inscripciones`

Mejora recomendada: devolver inscripciones con datos del alumno, grupo, carrera, cuatrimestre y periodo.

Relaciones a cargar:

- `Inscripcion.alumno`
- `Alumno.usuario`
- `Inscripcion.grupo`
- `Grupo.carrera`
- `Grupo.cuatrimestre`
- `Inscripcion.periodo`

Filtros utiles:

- `GET /inscripciones?alumno_id=1`
- `GET /inscripciones?grupo_id=1`
- `GET /inscripciones?periodo_id=1`
- `GET /inscripciones?estado=ACTIVO`

### `GET /historiales-academicos`

Mejora recomendada: devolver historial con alumno, materia y periodo. Tambien conviene ordenar por fecha de cierre descendente.

Relaciones a cargar:

- `HistorialAcademico.alumno`
- `Alumno.usuario`
- `HistorialAcademico.materia`
- `HistorialAcademico.periodo`

Filtros utiles:

- `GET /historiales-academicos?alumno_id=1`
- `GET /historiales-academicos?materia_id=1`
- `GET /historiales-academicos?periodo_id=1`
- `GET /historiales-academicos?resultado=APROBADO`
- `GET /historiales-academicos?tipo_evaluacion=ORDINARIO`

### `GET /calificaciones`

Aunque ya existia antes, conviene mejorar este GET porque depende de `CargaAcademica`.

Relaciones a cargar:

- `Calificacion.carga`
- `CargaAcademica.alumno`
- `Alumno.usuario`
- `CargaAcademica.grupo_materia`
- `GrupoMateria.materia`
- `Calificacion.parcial`
- `Calificacion.usuario`

Filtros utiles:

- `GET /calificaciones?alumno_id=1`
- `GET /calificaciones?materia_id=6`
- `GET /calificaciones?grupo_id=1`
- `GET /calificaciones?periodo_id=1`
- `GET /calificaciones?parcial_id=1`

### `GET /documentos-alumno`

Mejora recomendada: devolver documento con alumno y tipo de documento.

Relaciones a cargar:

- `DocumentoAlumno.alumno`
- `Alumno.usuario`
- `DocumentoAlumno.tipo_documento`

Filtros utiles:

- `GET /documentos-alumno?alumno_id=1`
- `GET /documentos-alumno?tipo_documento_id=1`
- `GET /documentos-alumno?validado=true`

### `GET /recepciones-documento`

Mejora recomendada: devolver la recepcion con datos del alumno y del usuario que recibio documentos.

Relaciones a cargar:

- `RecepcionDocumento.alumno`
- `Alumno.usuario`
- `RecepcionDocumento.usuario`

Filtros utiles:

- `GET /recepciones-documento?alumno_id=1`
- `GET /recepciones-documento?recibido_por=4`
- `GET /recepciones-documento?fecha_inicio=2026-01-01&fecha_fin=2026-01-31`

### `GET /contactos-emergencia`, `/seguros-medicos` y `/procedencias-academicas`

Mejora recomendada: en estos tres endpoints casi siempre se consulta por alumno, no por listado general.

Endpoints utiles:

- `GET /alumnos/{alumno_id}/contactos-emergencia`
- `GET /alumnos/{alumno_id}/seguros-medicos`
- `GET /alumnos/{alumno_id}/procedencia-academica`

Tambien se puede mantener el listado global para administracion, pero el uso principal sera por expediente del alumno.

### `GET /servicios-sociales` y `/practicas-profesionales`

Mejora recomendada: devolver alumno y empresa, y permitir filtrar por estado.

Relaciones a cargar:

- `ServicioSocial.alumno`
- `ServicioSocial.empresa`
- `PracticaProfesional.alumno`
- `PracticaProfesional.empresa`

Filtros utiles:

- `GET /servicios-sociales?alumno_id=1`
- `GET /servicios-sociales?empresa_id=1`
- `GET /servicios-sociales?estado=EN_PROCESO`
- `GET /practicas-profesionales?alumno_id=1`
- `GET /practicas-profesionales?empresa_id=2`
- `GET /practicas-profesionales?estado=EN_PROCESO`

### `GET /alumnos-tutores` y `/usuarios-roles`

Mejora recomendada: estas tablas pivote no deberian quedarse solo con IDs en respuestas de lectura.

Para `alumnos-tutores`, devolver:

- Alumno: `id_alumno`, `matricula`, nombre completo desde `Usuario`.
- Tutor: `id_tutor`, `nombre`, `parentesco`, `telefono`.

Para `usuarios-roles`, devolver:

- Usuario: `id_usuario`, nombre completo, correo.
- Rol: `id_rol`, `nombre`.

Endpoints utiles:

- `GET /alumnos/{alumno_id}/tutores`
- `GET /tutores/{tutor_id}/alumnos`
- `GET /usuarios/{usuario_id}/roles`
- `GET /roles/{rol_id}/usuarios`

### Recomendacion tecnica general

Para evitar consultas N+1 en estos GET, conviene implementar funciones especificas en CRUD usando `joinedload` o `selectinload`, por ejemplo:

```python
db.query(Asistencia).options(
    joinedload(Asistencia.carga)
    .joinedload(CargaAcademica.alumno)
    .joinedload(Alumno.usuario),
    joinedload(Asistencia.carga)
    .joinedload(CargaAcademica.grupo_materia)
    .joinedload(GrupoMateria.materia)
)
```

Tambien conviene crear schemas de respuesta tipo `Detalle`, por ejemplo `AsistenciaDetalleResponse`, `CargaAcademicaDetalleResponse` y `GrupoMateriaDetalleResponse`, para no romper los responses simples que ya existen.
