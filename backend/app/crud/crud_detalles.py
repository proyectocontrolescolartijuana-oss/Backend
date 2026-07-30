from sqlalchemy.orm import Session, joinedload

from app.models.alumno import Alumno
from app.models.alumno_tutor import alumno_tutor
from app.models.asistencia import Asistencia
from app.models.calificacion import Calificacion
from app.models.carga_academica import CargaAcademica
from app.models.contacto_emergencia import ContactoEmergencia
from app.models.documento_alumno import DocumentoAlumno
from app.models.docente import Docente
from app.models.grupo import Grupo
from app.models.grupo_materia import GrupoMateria
from app.models.historial_academico import HistorialAcademico
from app.models.inscripcion import Inscripcion
from app.models.materia import Materia
from app.models.practica_profesional import PracticaProfesional
from app.models.procedencia_academica import ProcedenciaAcademica
from app.models.recepcion_documento import RecepcionDocumento
from app.models.rol import Rol
from app.models.seguro_medico import SeguroMedico
from app.models.servicio_social import ServicioSocial
from app.models.tutor import Tutor
from app.models.usuario import Usuario
from app.models.usuario_rol import usuario_roles


def _nombre_usuario(usuario):
    if not usuario:
        return None

    partes = [
        usuario.apellido_paterno,
        usuario.apellido_materno,
        usuario.nombre
    ]

    return " ".join(parte for parte in partes if parte)


def _usuario(usuario):
    if not usuario:
        return None

    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido_paterno": usuario.apellido_paterno,
        "apellido_materno": usuario.apellido_materno,
        "correo": usuario.correo
    }


def _alumno(alumno):
    if not alumno:
        return None

    return {
        "id_alumno": alumno.id_alumno,
        "matricula": alumno.matricula,
        "numero_control": alumno.numero_control,
        "nombre": _nombre_usuario(alumno.usuario)
    }


def _docente(docente):
    if not docente:
        return None

    return {
        "id_docente": docente.id_docente,
        "numero_empleado": docente.numero_empleado,
        "nombre": _nombre_usuario(docente.usuario)
    }


def _materia(materia):
    if not materia:
        return None

    return {
        "id_materia": materia.id_materia,
        "clave": materia.clave,
        "nombre": materia.nombre,
        "creditos": float(materia.creditos) if materia.creditos is not None else None
    }


def _grupo(grupo):
    if not grupo:
        return None

    return {
        "id_grupo": grupo.id_grupo,
        "nombre": grupo.nombre,
        "turno": grupo.turno,
        "id_carrera": grupo.id_carrera,
        "id_plan": grupo.id_plan,
        "estatus": grupo.estatus,
        "cuatrimestre": _cuatrimestre(grupo.cuatrimestre)
    }


def _periodo(periodo):
    if not periodo:
        return None

    return {
        "id_periodo": periodo.id_periodo,
        "nombre": periodo.nombre,
        "estado": periodo.estado
    }


def _carrera(carrera):
    if not carrera:
        return None

    return {
        "id_carrera": carrera.id_carrera,
        "clave": carrera.clave,
        "rvoe": carrera.rvoe,
        "nombre": carrera.nombre
    }


def _cuatrimestre(cuatrimestre):
    if not cuatrimestre:
        return None

    return {
        "id_cuatrimestre": cuatrimestre.id_cuatrimestre,
        "numero": cuatrimestre.numero,
        "nombre": cuatrimestre.nombre
    }


def _empresa(empresa):
    if not empresa:
        return None

    return {
        "id_empresa": empresa.id_empresa,
        "nombre": empresa.nombre,
        "telefono": empresa.telefono,
        "correo": empresa.correo
    }


def _tutor(tutor):
    if not tutor:
        return None

    return {
        "id_tutor": tutor.id_tutor,
        "nombre": tutor.nombre,
        "parentesco": tutor.parentesco,
        "telefono": tutor.telefono,
        "correo": tutor.correo
    }


def _grupo_materia(grupo_materia):
    if not grupo_materia:
        return None

    return {
        "id_grupo_materia": grupo_materia.id_grupo_materia,
        "aula": grupo_materia.aula,
        "cupo_maximo": grupo_materia.cupo_maximo,
        "grupo": _grupo(grupo_materia.grupo),
        "materia": _materia(grupo_materia.materia),
        "docente": _docente(grupo_materia.docente),
        "periodo": _periodo(grupo_materia.periodo)
    }


def _carga(carga):
    if not carga:
        return None

    return {
        "id_carga": carga.id_carga,
        "oportunidad": carga.oportunidad,
        "intento": carga.intento,
        "estatus": carga.estatus,
        "fecha_inscripcion": carga.fecha_inscripcion,
        "alumno": _alumno(carga.alumno),
        "grupo_materia": _grupo_materia(carga.grupo_materia)
    }


def _apply_carga_filters(
    query,
    *,
    alumno_id=None,
    grupo_materia_id=None,
    grupo_id=None,
    docente_id=None,
    materia_id=None,
    periodo_id=None,
    estatus=None
):
    if alumno_id is not None:
        query = query.filter(CargaAcademica.id_alumno == alumno_id)
    if grupo_materia_id is not None:
        query = query.filter(CargaAcademica.id_grupo_materia == grupo_materia_id)
    if estatus is not None:
        query = query.filter(CargaAcademica.estatus == estatus)
    if any(value is not None for value in [grupo_id, docente_id, materia_id, periodo_id]):
        query = query.join(CargaAcademica.grupo_materia)
    if grupo_id is not None:
        query = query.filter(GrupoMateria.id_grupo == grupo_id)
    if docente_id is not None:
        query = query.filter(GrupoMateria.id_docente == docente_id)
    if materia_id is not None:
        query = query.filter(GrupoMateria.id_materia == materia_id)
    if periodo_id is not None:
        query = query.filter(GrupoMateria.id_periodo == periodo_id)

    return query


def get_cargas_academicas_detalle(
    db: Session,
    alumno_id=None,
    grupo_materia_id=None,
    grupo_id=None,
    docente_id=None,
    materia_id=None,
    periodo_id=None,
    estatus=None
):
    query = db.query(CargaAcademica).options(
        joinedload(CargaAcademica.alumno).joinedload(Alumno.usuario),
        joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.materia),
        joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.grupo),
        joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.periodo),
        joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.docente)
        .joinedload(Docente.usuario)
    )

    query = _apply_carga_filters(
        query,
        alumno_id=alumno_id,
        grupo_materia_id=grupo_materia_id,
        grupo_id=grupo_id,
        docente_id=docente_id,
        materia_id=materia_id,
        periodo_id=periodo_id,
        estatus=estatus
    )

    return [_carga(carga) for carga in query.all()]


def get_carga_academica_detalle(db: Session, carga_id: int):
    carga = (
        db.query(CargaAcademica)
        .options(
            joinedload(CargaAcademica.alumno).joinedload(Alumno.usuario),
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.materia),
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.grupo),
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.periodo),
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.docente)
            .joinedload(Docente.usuario)
        )
        .filter(CargaAcademica.id_carga == carga_id)
        .first()
    )

    return _carga(carga)


def get_asistencias_detalle(
    db: Session,
    alumno_id=None,
    grupo_id=None,
    materia_id=None,
    periodo_id=None,
    fecha_inicio=None,
    fecha_fin=None
):
    query = db.query(Asistencia).options(
        joinedload(Asistencia.carga)
        .joinedload(CargaAcademica.alumno)
        .joinedload(Alumno.usuario),
        joinedload(Asistencia.carga)
        .joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.materia),
        joinedload(Asistencia.carga)
        .joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.grupo),
        joinedload(Asistencia.carga)
        .joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.periodo)
    )

    if fecha_inicio is not None:
        query = query.filter(Asistencia.fecha >= fecha_inicio)
    if fecha_fin is not None:
        query = query.filter(Asistencia.fecha <= fecha_fin)
    if any(value is not None for value in [alumno_id, grupo_id, materia_id, periodo_id]):
        query = query.join(Asistencia.carga)
    if alumno_id is not None:
        query = query.filter(CargaAcademica.id_alumno == alumno_id)
    if any(value is not None for value in [grupo_id, materia_id, periodo_id]):
        query = query.join(CargaAcademica.grupo_materia)
    if grupo_id is not None:
        query = query.filter(GrupoMateria.id_grupo == grupo_id)
    if materia_id is not None:
        query = query.filter(GrupoMateria.id_materia == materia_id)
    if periodo_id is not None:
        query = query.filter(GrupoMateria.id_periodo == periodo_id)

    return [_asistencia(asistencia) for asistencia in query.all()]


def get_asistencia_detalle(db: Session, asistencia_id: int):
    asistencia = (
        db.query(Asistencia)
        .options(
            joinedload(Asistencia.carga)
            .joinedload(CargaAcademica.alumno)
            .joinedload(Alumno.usuario),
            joinedload(Asistencia.carga)
            .joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.materia),
            joinedload(Asistencia.carga)
            .joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.grupo),
            joinedload(Asistencia.carga)
            .joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.periodo)
        )
        .filter(Asistencia.id_asistencia == asistencia_id)
        .first()
    )

    return _asistencia(asistencia)


def _asistencia(asistencia):
    if not asistencia:
        return None

    grupo_materia = asistencia.carga.grupo_materia if asistencia.carga else None

    return {
        "id_asistencia": asistencia.id_asistencia,
        "fecha": asistencia.fecha,
        "asistencia": asistencia.asistencia,
        "alumno": _alumno(asistencia.carga.alumno) if asistencia.carga else None,
        "materia": _materia(grupo_materia.materia) if grupo_materia else None,
        "grupo": _grupo(grupo_materia.grupo) if grupo_materia else None,
        "periodo": _periodo(grupo_materia.periodo) if grupo_materia else None
    }


def get_grupos_materias_detalle(
    db: Session,
    grupo_id=None,
    carrera_id=None,
    docente_id=None,
    materia_id=None,
    periodo_id=None
):
    query = db.query(GrupoMateria).options(
        joinedload(GrupoMateria.grupo).joinedload(Grupo.cuatrimestre),
        joinedload(GrupoMateria.materia),
        joinedload(GrupoMateria.docente).joinedload(Docente.usuario),
        joinedload(GrupoMateria.periodo)
    )

    if grupo_id is not None:
        query = query.filter(GrupoMateria.id_grupo == grupo_id)
    if carrera_id is not None:
        query = query.join(GrupoMateria.grupo)
        query = query.filter(Grupo.id_carrera == carrera_id)
    if docente_id is not None:
        query = query.filter(GrupoMateria.id_docente == docente_id)
    if materia_id is not None:
        query = query.filter(GrupoMateria.id_materia == materia_id)
    if periodo_id is not None:
        query = query.filter(GrupoMateria.id_periodo == periodo_id)

    return [_grupo_materia(grupo_materia) for grupo_materia in query.all()]


def get_grupo_materia_detalle(db: Session, grupo_materia_id: int):
    grupo_materia = (
        db.query(GrupoMateria)
        .options(
            joinedload(GrupoMateria.grupo).joinedload(Grupo.cuatrimestre),
            joinedload(GrupoMateria.materia),
            joinedload(GrupoMateria.docente).joinedload(Docente.usuario),
            joinedload(GrupoMateria.periodo)
        )
        .filter(GrupoMateria.id_grupo_materia == grupo_materia_id)
        .first()
    )

    return _grupo_materia(grupo_materia)


def get_inscripciones_detalle(
    db: Session,
    alumno_id=None,
    grupo_id=None,
    periodo_id=None,
    estado=None
):
    query = db.query(Inscripcion).options(
        joinedload(Inscripcion.alumno).joinedload(Alumno.usuario),
        joinedload(Inscripcion.grupo).joinedload(Grupo.carrera),
        joinedload(Inscripcion.grupo).joinedload(Grupo.cuatrimestre),
        joinedload(Inscripcion.periodo)
    )

    if alumno_id is not None:
        query = query.filter(Inscripcion.id_alumno == alumno_id)
    if grupo_id is not None:
        query = query.filter(Inscripcion.id_grupo == grupo_id)
    if periodo_id is not None:
        query = query.filter(Inscripcion.id_periodo == periodo_id)
    if estado is not None:
        query = query.filter(Inscripcion.estado == estado)

    return [_inscripcion(inscripcion) for inscripcion in query.all()]


def _inscripcion(inscripcion):
    if not inscripcion:
        return None

    return {
        "id_inscripcion": inscripcion.id_inscripcion,
        "fecha_inscripcion": inscripcion.fecha_inscripcion,
        "estado": inscripcion.estado,
        "alumno": _alumno(inscripcion.alumno),
        "grupo": _grupo(inscripcion.grupo),
        "carrera": _carrera(inscripcion.grupo.carrera) if inscripcion.grupo else None,
        "cuatrimestre": (
            _cuatrimestre(inscripcion.grupo.cuatrimestre)
            if inscripcion.grupo else None
        ),
        "periodo": _periodo(inscripcion.periodo)
    }


def get_historiales_academicos_detalle(
    db: Session,
    alumno_id=None,
    materia_id=None,
    periodo_id=None,
    resultado=None,
    tipo_evaluacion=None,
    carrera_id=None,
):
    query = db.query(HistorialAcademico).options(
        joinedload(HistorialAcademico.alumno).joinedload(Alumno.usuario),
        joinedload(HistorialAcademico.alumno).joinedload(Alumno.carrera),
        joinedload(HistorialAcademico.materia),
        joinedload(HistorialAcademico.periodo)
    )


    if alumno_id is not None:
        query = query.filter(HistorialAcademico.id_alumno == alumno_id)
    if materia_id is not None:
        query = query.filter(HistorialAcademico.id_materia == materia_id)
    if periodo_id is not None:
        query = query.filter(HistorialAcademico.id_periodo == periodo_id)
    if resultado is not None:
        query = query.filter(HistorialAcademico.resultado == resultado)
    if tipo_evaluacion is not None:
        query = query.filter(HistorialAcademico.tipo_evaluacion == tipo_evaluacion)
    if carrera_id is not None:
        query = query.join(HistorialAcademico.alumno)
        query = query.filter(Alumno.id_carrera == carrera_id)


    return [
        _historial(historial)
        for historial in query.order_by(HistorialAcademico.fecha_cierre.desc()).all()
    ]


def _historial(historial):
    if not historial:
        return None

    return {
        "id_historial": historial.id_historial,
        "tipo_evaluacion": historial.tipo_evaluacion,
        "oportunidad": historial.oportunidad,
        "calificacion_final": (
            float(historial.calificacion_final)
            if historial.calificacion_final is not None else None
        ),
        "resultado": historial.resultado,
        "fecha_cierre": historial.fecha_cierre,
        "alumno": _alumno(historial.alumno),
        "carrera": _carrera(historial.alumno.carrera) if historial.alumno else None,
        "materia": _materia(historial.materia),
        "periodo": _periodo(historial.periodo)
    }



def get_calificaciones_detalle(
    db: Session,
    alumno_id=None,
    materia_id=None,
    grupo_id=None,
    periodo_id=None,
    parcial_id=None
):
    query = db.query(Calificacion).options(
        joinedload(Calificacion.carga)
        .joinedload(CargaAcademica.alumno)
        .joinedload(Alumno.usuario),
        joinedload(Calificacion.carga)
        .joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.materia),
        joinedload(Calificacion.carga)
        .joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.grupo),
        joinedload(Calificacion.carga)
        .joinedload(CargaAcademica.grupo_materia)
        .joinedload(GrupoMateria.periodo),
        joinedload(Calificacion.parcial),
        joinedload(Calificacion.usuario)
    )

    if parcial_id is not None:
        query = query.filter(Calificacion.id_parcial == parcial_id)
    if any(value is not None for value in [alumno_id, materia_id, grupo_id, periodo_id]):
        query = query.join(Calificacion.carga)
    if alumno_id is not None:
        query = query.filter(CargaAcademica.id_alumno == alumno_id)
    if any(value is not None for value in [materia_id, grupo_id, periodo_id]):
        query = query.join(CargaAcademica.grupo_materia)
    if materia_id is not None:
        query = query.filter(GrupoMateria.id_materia == materia_id)
    if grupo_id is not None:
        query = query.filter(GrupoMateria.id_grupo == grupo_id)
    if periodo_id is not None:
        query = query.filter(GrupoMateria.id_periodo == periodo_id)

    return [_calificacion(calificacion) for calificacion in query.all()]


def _calificacion(calificacion):
    if not calificacion:
        return None

    grupo_materia = calificacion.carga.grupo_materia if calificacion.carga else None

    return {
        "id_calificacion": calificacion.id_calificacion,
        "calificacion": (
            float(calificacion.calificacion)
            if calificacion.calificacion is not None else None
        ),
        "alumno": _alumno(calificacion.carga.alumno) if calificacion.carga else None,
        "materia": _materia(grupo_materia.materia) if grupo_materia else None,
        "grupo": _grupo(grupo_materia.grupo) if grupo_materia else None,
        "periodo": _periodo(grupo_materia.periodo) if grupo_materia else None,
        "parcial": {
            "id_parcial": calificacion.parcial.id_parcial,
            "nombre": calificacion.parcial.nombre,
            "porcentaje": (
                float(calificacion.parcial.porcentaje)
                if calificacion.parcial.porcentaje is not None else None
            )
        } if calificacion.parcial else None,
        "capturado_por": _usuario(calificacion.usuario)
    }


def get_documentos_alumno_detalle(db: Session, alumno_id=None, tipo_documento_id=None, validado=None):
    query = db.query(DocumentoAlumno).options(
        joinedload(DocumentoAlumno.alumno).joinedload(Alumno.usuario),
        joinedload(DocumentoAlumno.tipo_documento)
    )

    if alumno_id is not None:
        query = query.filter(DocumentoAlumno.id_alumno == alumno_id)
    if tipo_documento_id is not None:
        query = query.filter(DocumentoAlumno.id_tipo_documento == tipo_documento_id)
    if validado is not None:
        query = query.filter(DocumentoAlumno.validado == validado)

    return [_documento_alumno(documento) for documento in query.all()]


def _documento_alumno(documento):
    if not documento:
        return None

    return {
        "id_documento": documento.id_documento,
        "nombre_archivo": documento.nombre_archivo,
        "ruta_archivo": documento.ruta_archivo,
        "validado": documento.validado,
        "observaciones": documento.observaciones,
        "alumno": _alumno(documento.alumno),
        "tipo_documento": {
            "id_tipo_documento": documento.tipo_documento.id_tipo_documento,
            "nombre": documento.tipo_documento.nombre
        } if documento.tipo_documento else None
    }


def get_recepciones_documento_detalle(
    db: Session,
    alumno_id=None,
    recibido_por=None,
    fecha_inicio=None,
    fecha_fin=None
):
    query = db.query(RecepcionDocumento).options(
        joinedload(RecepcionDocumento.alumno).joinedload(Alumno.usuario),
        joinedload(RecepcionDocumento.usuario)
    )

    if alumno_id is not None:
        query = query.filter(RecepcionDocumento.id_alumno == alumno_id)
    if recibido_por is not None:
        query = query.filter(RecepcionDocumento.recibido_por == recibido_por)
    if fecha_inicio is not None:
        query = query.filter(RecepcionDocumento.fecha_recepcion >= fecha_inicio)
    if fecha_fin is not None:
        query = query.filter(RecepcionDocumento.fecha_recepcion <= fecha_fin)

    return [_recepcion_documento(recepcion) for recepcion in query.all()]


def _recepcion_documento(recepcion):
    if not recepcion:
        return None

    return {
        "id_recepcion": recepcion.id_recepcion,
        "fecha_recepcion": recepcion.fecha_recepcion,
        "ficha_inscripcion": recepcion.ficha_inscripcion,
        "acta_original": recepcion.acta_original,
        "acta_copias": recepcion.acta_copias,
        "certificado_original": recepcion.certificado_original,
        "constancia_terminacion": recepcion.constancia_terminacion,
        "fotografias": recepcion.fotografias,
        "curp_documento": recepcion.curp_documento,
        "observaciones": recepcion.observaciones,
        "alumno": _alumno(recepcion.alumno),
        "recibido_por": _usuario(recepcion.usuario)
    }


def get_contactos_emergencia_detalle(db: Session, alumno_id=None):
    query = db.query(ContactoEmergencia).options(
        joinedload(ContactoEmergencia.alumno).joinedload(Alumno.usuario)
    )

    if alumno_id is not None:
        query = query.filter(ContactoEmergencia.id_alumno == alumno_id)

    return [
        {
            "id_contacto": contacto.id_contacto,
            "nombre": contacto.nombre,
            "parentesco": contacto.parentesco,
            "telefono": contacto.telefono,
            "correo": contacto.correo,
            "direccion": contacto.direccion,
            "contacto_principal": contacto.contacto_principal,
            "alumno": _alumno(contacto.alumno)
        }
        for contacto in query.all()
    ]


def get_seguros_medicos_detalle(db: Session, alumno_id=None):
    query = db.query(SeguroMedico).options(
        joinedload(SeguroMedico.alumno).joinedload(Alumno.usuario)
    )

    if alumno_id is not None:
        query = query.filter(SeguroMedico.id_alumno == alumno_id)

    return [
        {
            "id_seguro": seguro.id_seguro,
            "tiene_seguro": seguro.tiene_seguro,
            "institucion": seguro.institucion,
            "numero_poliza": seguro.numero_poliza,
            "alumno": _alumno(seguro.alumno)
        }
        for seguro in query.all()
    ]


def get_procedencias_academicas_detalle(db: Session, alumno_id=None):
    query = db.query(ProcedenciaAcademica).options(
        joinedload(ProcedenciaAcademica.alumno).joinedload(Alumno.usuario)
    )

    if alumno_id is not None:
        query = query.filter(ProcedenciaAcademica.id_alumno == alumno_id)

    return [
        {
            "id_procedencia": procedencia.id_procedencia,
            "escuela_procedencia": procedencia.escuela_procedencia,
            "nivel_academico": procedencia.nivel_academico,
            "estado_procedencia": procedencia.estado_procedencia,
            "promedio_general": (
                float(procedencia.promedio_general)
                if procedencia.promedio_general is not None else None
            ),
            "fecha_egreso": procedencia.fecha_egreso,
            "alumno": _alumno(procedencia.alumno)
        }
        for procedencia in query.all()
    ]


def get_servicios_sociales_detalle(db: Session, alumno_id=None, empresa_id=None, estado=None):
    query = db.query(ServicioSocial).options(
        joinedload(ServicioSocial.alumno).joinedload(Alumno.usuario),
        joinedload(ServicioSocial.empresa)
    )

    if alumno_id is not None:
        query = query.filter(ServicioSocial.id_alumno == alumno_id)
    if empresa_id is not None:
        query = query.filter(ServicioSocial.id_empresa == empresa_id)
    if estado is not None:
        query = query.filter(ServicioSocial.estado == estado)

    return [
        {
            "id_servicio": servicio.id_servicio,
            "horas_requeridas": servicio.horas_requeridas,
            "horas_completadas": servicio.horas_completadas,
            "fecha_inicio": servicio.fecha_inicio,
            "fecha_fin": servicio.fecha_fin,
            "estado": servicio.estado,
            "carta_unifront": servicio.carta_unifront,
            "carta_procedencia": servicio.carta_procedencia,
            "alumno": _alumno(servicio.alumno),
            "empresa": _empresa(servicio.empresa)
        }
        for servicio in query.all()
    ]


def get_practicas_profesionales_detalle(db: Session, alumno_id=None, empresa_id=None, estado=None):
    query = db.query(PracticaProfesional).options(
        joinedload(PracticaProfesional.alumno).joinedload(Alumno.usuario),
        joinedload(PracticaProfesional.empresa)
    )

    if alumno_id is not None:
        query = query.filter(PracticaProfesional.id_alumno == alumno_id)
    if empresa_id is not None:
        query = query.filter(PracticaProfesional.id_empresa == empresa_id)
    if estado is not None:
        query = query.filter(PracticaProfesional.estado == estado)

    return [
        {
            "id_practica": practica.id_practica,
            "proyecto": practica.proyecto,
            "asesor_empresa": practica.asesor_empresa,
            "asesor_universidad": practica.asesor_universidad,
            "fecha_inicio": practica.fecha_inicio,
            "fecha_fin": practica.fecha_fin,
            "estado": practica.estado,
            "oficio_campo": practica.oficio_campo,
            "horas_campo": practica.horas_campo,
            "alumno": _alumno(practica.alumno),
            "empresa": _empresa(practica.empresa)
        }
        for practica in query.all()
    ]


def get_alumnos_tutores_detalle(db: Session):
    rows = (
        db.query(Alumno, Tutor)
        .join(alumno_tutor, Alumno.id_alumno == alumno_tutor.c.id_alumno)
        .join(Tutor, Tutor.id_tutor == alumno_tutor.c.id_tutor)
        .options(joinedload(Alumno.usuario))
        .all()
    )

    return [
        {
            "alumno": _alumno(alumno),
            "tutor": _tutor(tutor)
        }
        for alumno, tutor in rows
    ]


def get_tutores_por_alumno(db: Session, alumno_id: int):
    rows = (
        db.query(Tutor)
        .join(alumno_tutor, Tutor.id_tutor == alumno_tutor.c.id_tutor)
        .filter(alumno_tutor.c.id_alumno == alumno_id)
        .all()
    )

    return [{"tutor": _tutor(tutor)} for tutor in rows]


def get_alumnos_por_tutor(db: Session, tutor_id: int):
    rows = (
        db.query(Alumno)
        .join(alumno_tutor, Alumno.id_alumno == alumno_tutor.c.id_alumno)
        .options(joinedload(Alumno.usuario))
        .filter(alumno_tutor.c.id_tutor == tutor_id)
        .all()
    )

    return [{"alumno": _alumno(alumno)} for alumno in rows]


def get_usuarios_roles_detalle(db: Session):
    rows = (
        db.query(Usuario, Rol)
        .join(usuario_roles, Usuario.id_usuario == usuario_roles.c.id_usuario)
        .join(Rol, Rol.id_rol == usuario_roles.c.id_rol)
        .all()
    )

    return [
        {
            "usuario": _usuario(usuario),
            "rol": {
                "id_rol": rol.id_rol,
                "nombre": rol.nombre
            }
        }
        for usuario, rol in rows
    ]
