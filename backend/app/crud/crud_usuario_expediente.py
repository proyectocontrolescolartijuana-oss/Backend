from sqlalchemy.orm import Session, joinedload

from app.crud.crud_detalles import (
    get_calificaciones_detalle,
    get_cargas_academicas_detalle,
    get_documentos_alumno_detalle,
    get_historiales_academicos_detalle,
    get_inscripciones_detalle,
    get_practicas_profesionales_detalle,
    get_recepciones_documento_detalle,
    get_servicios_sociales_detalle
)
from app.models.alumno import Alumno
from app.models.alumno_tutor import alumno_tutor
from app.models.contacto_emergencia import ContactoEmergencia
from app.models.docente import Docente
from app.models.procedencia_academica import ProcedenciaAcademica
from app.models.seguro_medico import SeguroMedico
from app.models.titulacion import Titulacion
from app.models.tutor import Tutor
from app.models.usuario import Usuario


def _float(value):
    return float(value) if value is not None else None


def _rol(rol):
    return {
        "id_rol": rol.id_rol,
        "nombre": rol.nombre
    }


def _usuario(usuario):
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido_paterno": usuario.apellido_paterno,
        "apellido_materno": usuario.apellido_materno,
        "correo": usuario.correo,
        "telefono": usuario.telefono,
        "estado": usuario.estado,
        "fecha_creacion": usuario.fecha_creacion,
        "roles": [_rol(rol) for rol in usuario.roles]
    }


def _carrera(carrera):
    if not carrera:
        return None

    return {
        "id_carrera": carrera.id_carrera,
        "clave": carrera.clave,
        "rvoe": carrera.rvoe,
        "nombre": carrera.nombre,
        "nivel": carrera.nivel,
        "duracion_cuatrimestres": carrera.duracion_cuatrimestres,
        "estado": carrera.estado
    }


def _plan(plan):
    if not plan:
        return None

    return {
        "id_plan": plan.id_plan,
        "id_carrera": plan.id_carrera,
        "nombre_plan": plan.nombre_plan,
        "fecha_inicio": plan.fecha_inicio,
        "fecha_fin": plan.fecha_fin,
        "vigente": plan.vigente
    }


def _alumno(alumno):
    if not alumno:
        return None

    return {
        "id_alumno": alumno.id_alumno,
        "matricula": alumno.matricula,
        "numero_control": alumno.numero_control,
        "id_usuario": alumno.id_usuario,
        "id_carrera": alumno.id_carrera,
        "id_plan": alumno.id_plan,
        "fecha_nacimiento": alumno.fecha_nacimiento,
        "ciudad_nacimiento": alumno.ciudad_nacimiento,
        "municipio_nacimiento": alumno.municipio_nacimiento,
        "nacionalidad": alumno.nacionalidad,
        "sexo": alumno.sexo,
        "curp": alumno.curp,
        "direccion": alumno.direccion,
        "ciudad": alumno.ciudad,
        "estado": alumno.estado,
        "correo_contacto": alumno.correo_contacto,
        "fecha_ingreso": alumno.fecha_ingreso,
        "estatus": alumno.estatus,
        "foto": alumno.foto,
        "carrera": _carrera(alumno.carrera),
        "plan": _plan(alumno.plan)
    }


def _docente(docente):
    if not docente:
        return None

    return {
        "id_docente": docente.id_docente,
        "id_usuario": docente.id_usuario,
        "numero_empleado": docente.numero_empleado,
        "especialidad": docente.especialidad,
        "grado_academico": docente.grado_academico,
        "fecha_ingreso": docente.fecha_ingreso,
        "estado": docente.estado
    }


def _tutor(tutor):
    return {
        "id_tutor": tutor.id_tutor,
        "nombre": tutor.nombre,
        "parentesco": tutor.parentesco,
        "telefono": tutor.telefono,
        "correo": tutor.correo,
        "ocupacion": tutor.ocupacion
    }


def _contacto(contacto):
    return {
        "id_contacto": contacto.id_contacto,
        "id_alumno": contacto.id_alumno,
        "nombre": contacto.nombre,
        "parentesco": contacto.parentesco,
        "telefono": contacto.telefono,
        "correo": contacto.correo,
        "direccion": contacto.direccion,
        "contacto_principal": contacto.contacto_principal
    }


def _seguro(seguro):
    return {
        "id_seguro": seguro.id_seguro,
        "id_alumno": seguro.id_alumno,
        "tiene_seguro": seguro.tiene_seguro,
        "institucion": seguro.institucion,
        "numero_poliza": seguro.numero_poliza
    }


def _procedencia(procedencia):
    if not procedencia:
        return None

    return {
        "id_procedencia": procedencia.id_procedencia,
        "id_alumno": procedencia.id_alumno,
        "escuela_procedencia": procedencia.escuela_procedencia,
        "nivel_academico": procedencia.nivel_academico,
        "estado_procedencia": procedencia.estado_procedencia,
        "promedio_general": _float(procedencia.promedio_general),
        "fecha_egreso": procedencia.fecha_egreso
    }


def _titulacion(titulacion):
    return {
        "id_titulacion": titulacion.id_titulacion,
        "id_alumno": titulacion.id_alumno,
        "modalidad": titulacion.modalidad,
        "cumple_promedio": titulacion.cumple_promedio,
        "servicio_social_liberado": titulacion.servicio_social_liberado,
        "practicas_liberadas": titulacion.practicas_liberadas,
        "certificado_emitido": titulacion.certificado_emitido,
        "pagos_titulacion_completos": titulacion.pagos_titulacion_completos,
        "numero_autorizacion": titulacion.numero_autorizacion,
        "acta_examen": titulacion.acta_examen,
        "titulo_emitido": titulacion.titulo_emitido,
        "fecha_titulacion": titulacion.fecha_titulacion,
        "observaciones": titulacion.observaciones
    }


def _get_alumno(db: Session, usuario_id: int):
    return (
        db.query(Alumno)
        .options(
            joinedload(Alumno.carrera),
            joinedload(Alumno.plan)
        )
        .filter(Alumno.id_usuario == usuario_id)
        .first()
    )


def _get_docente(db: Session, usuario_id: int):
    return (
        db.query(Docente)
        .filter(Docente.id_usuario == usuario_id)
        .first()
    )


def _get_tutores(db: Session, alumno_id: int):
    return (
        db.query(Tutor)
        .join(alumno_tutor, Tutor.id_tutor == alumno_tutor.c.id_tutor)
        .filter(alumno_tutor.c.id_alumno == alumno_id)
        .all()
    )


def _get_contactos(db: Session, alumno_id: int):
    return (
        db.query(ContactoEmergencia)
        .filter(ContactoEmergencia.id_alumno == alumno_id)
        .order_by(ContactoEmergencia.contacto_principal.desc())
        .all()
    )


def _get_seguros(db: Session, alumno_id: int):
    return (
        db.query(SeguroMedico)
        .filter(SeguroMedico.id_alumno == alumno_id)
        .all()
    )


def _get_procedencia(db: Session, alumno_id: int):
    return (
        db.query(ProcedenciaAcademica)
        .filter(ProcedenciaAcademica.id_alumno == alumno_id)
        .first()
    )


def _get_titulaciones(db: Session, alumno_id: int):
    return (
        db.query(Titulacion)
        .filter(Titulacion.id_alumno == alumno_id)
        .all()
    )


def get_usuario_expediente(db: Session, usuario_id: int):
    usuario = (
        db.query(Usuario)
        .options(joinedload(Usuario.roles))
        .filter(Usuario.id_usuario == usuario_id)
        .first()
    )

    if not usuario:
        return None

    alumno = _get_alumno(db, usuario_id)
    docente = _get_docente(db, usuario_id)

    expediente_alumno = None

    if alumno:
        expediente_alumno = {
            "tutores": [_tutor(tutor) for tutor in _get_tutores(db, alumno.id_alumno)],
            "contactos_emergencia": [
                _contacto(contacto)
                for contacto in _get_contactos(db, alumno.id_alumno)
            ],
            "seguros_medicos": [
                _seguro(seguro)
                for seguro in _get_seguros(db, alumno.id_alumno)
            ],
            "procedencia_academica": _procedencia(
                _get_procedencia(db, alumno.id_alumno)
            ),
            "documentos_alumno": get_documentos_alumno_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "recepciones_documento": get_recepciones_documento_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "inscripciones": get_inscripciones_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "cargas_academicas": get_cargas_academicas_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "historial_academico": get_historiales_academicos_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "calificaciones": get_calificaciones_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "servicios_sociales": get_servicios_sociales_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "practicas_profesionales": get_practicas_profesionales_detalle(
                db,
                alumno_id=alumno.id_alumno
            ),
            "titulaciones": [
                _titulacion(titulacion)
                for titulacion in _get_titulaciones(db, alumno.id_alumno)
            ]
        }

    return {
        "usuario": _usuario(usuario),
        "alumno": _alumno(alumno),
        "docente": _docente(docente),
        "expediente_alumno": expediente_alumno
    }
