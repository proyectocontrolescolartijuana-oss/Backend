from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.database import get_db
from app.models.alumno import Alumno
from app.models.carrera import Carrera
from app.models.docente import Docente
from app.models.grupo import Grupo
from app.models.inscripcion import Inscripcion
from app.models.materia import Materia
from app.models.periodo import Periodo
from app.models.plan_estudio import PlanEstudio
from app.models.recepcion_documento import RecepcionDocumento
from app.models.usuario import Usuario
from app.services.excel_service import build_xlsx


ALLOWED_ROLES = {"ADMIN", "CONTROL_ESCOLAR"}
EXCEL_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

router = APIRouter(
    prefix="/reportes/fundamentales",
    tags=["Reportes"]
)


def _nombre_usuario(usuario: Usuario | None) -> str:
    if not usuario:
        return ""

    return " ".join(
        parte
        for parte in [
            usuario.nombre,
            usuario.apellido_paterno,
            usuario.apellido_materno
        ]
        if parte
    )


def _si_no(value) -> str:
    return "Si" if value else "No"


def _activo_inactivo(value) -> str:
    return "Activo" if value else "Inactivo"


def _marca(value) -> str:
    return "X" if value else ""


def _roles_usuario(usuario: Usuario) -> str:
    return ", ".join(sorted(rol.nombre for rol in usuario.roles))


def _require_reportes_role(usuario: Usuario = Depends(get_current_user)):
    roles = {rol.nombre for rol in usuario.roles}

    if roles.isdisjoint(ALLOWED_ROLES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consultar reportes"
        )

    return usuario


def _sheet_usuarios(db: Session) -> dict:
    usuarios = (
        db.query(Usuario)
        .options(joinedload(Usuario.roles))
        .order_by(Usuario.id_usuario)
        .all()
    )

    return {
        "name": "Usuarios",
        "columns": [
            {"key": "id_usuario", "header": "ID usuario"},
            {"key": "nombre", "header": "Nombre completo"},
            {"key": "correo", "header": "Correo"},
            {"key": "telefono", "header": "Telefono"},
            {"key": "estado", "header": "Estado"},
            {"key": "roles", "header": "Roles"},
            {"key": "fecha_creacion", "header": "Fecha creacion"},
        ],
        "rows": [
            {
                "id_usuario": usuario.id_usuario,
                "nombre": _nombre_usuario(usuario),
                "correo": usuario.correo,
                "telefono": usuario.telefono,
                "estado": usuario.estado,
                "roles": _roles_usuario(usuario),
                "fecha_creacion": usuario.fecha_creacion,
            }
            for usuario in usuarios
        ],
    }


def _sheet_alumnos(db: Session) -> dict:
    alumnos = (
        db.query(Alumno)
        .options(
            joinedload(Alumno.usuario),
            joinedload(Alumno.carrera),
            joinedload(Alumno.plan)
        )
        .order_by(Alumno.id_alumno)
        .all()
    )

    return {
        "name": "Alumnos",
        "columns": [
            {"key": "id_alumno", "header": "ID alumno"},
            {"key": "matricula", "header": "Matricula"},
            {"key": "numero_control", "header": "Numero control"},
            {"key": "nombre", "header": "Nombre completo"},
            {"key": "correo", "header": "Correo institucional"},
            {"key": "telefono", "header": "Telefono"},
            {"key": "carrera", "header": "Carrera"},
            {"key": "plan", "header": "Plan de estudio"},
            {"key": "fecha_nacimiento", "header": "Fecha nacimiento"},
            {"key": "sexo", "header": "Sexo"},
            {"key": "curp", "header": "CURP"},
            {"key": "ciudad", "header": "Ciudad"},
            {"key": "estado", "header": "Estado"},
            {"key": "fecha_ingreso", "header": "Fecha ingreso"},
            {"key": "estatus", "header": "Estatus"},
        ],
        "rows": [
            {
                "id_alumno": alumno.id_alumno,
                "matricula": alumno.matricula,
                "numero_control": alumno.numero_control,
                "nombre": _nombre_usuario(alumno.usuario),
                "correo": alumno.usuario.correo if alumno.usuario else "",
                "telefono": alumno.usuario.telefono if alumno.usuario else "",
                "carrera": alumno.carrera.nombre if alumno.carrera else "",
                "plan": alumno.plan.nombre_plan if alumno.plan else "",
                "fecha_nacimiento": alumno.fecha_nacimiento,
                "sexo": alumno.sexo,
                "curp": alumno.curp,
                "ciudad": alumno.ciudad,
                "estado": alumno.estado,
                "fecha_ingreso": alumno.fecha_ingreso,
                "estatus": alumno.estatus,
            }
            for alumno in alumnos
        ],
    }


def _sheet_docentes(db: Session) -> dict:
    docentes = (
        db.query(Docente)
        .options(joinedload(Docente.usuario))
        .order_by(Docente.id_docente)
        .all()
    )

    return {
        "name": "Docentes",
        "columns": [
            {"key": "id_docente", "header": "ID docente"},
            {"key": "numero_empleado", "header": "Numero empleado"},
            {"key": "nombre", "header": "Nombre completo"},
            {"key": "correo", "header": "Correo"},
            {"key": "telefono", "header": "Telefono"},
            {"key": "especialidad", "header": "Especialidad"},
            {"key": "grado_academico", "header": "Grado academico"},
            {"key": "fecha_ingreso", "header": "Fecha ingreso"},
            {"key": "estado", "header": "Estado"},
        ],
        "rows": [
            {
                "id_docente": docente.id_docente,
                "numero_empleado": docente.numero_empleado,
                "nombre": _nombre_usuario(docente.usuario),
                "correo": docente.usuario.correo if docente.usuario else "",
                "telefono": docente.usuario.telefono if docente.usuario else "",
                "especialidad": docente.especialidad,
                "grado_academico": docente.grado_academico,
                "fecha_ingreso": docente.fecha_ingreso,
                "estado": _activo_inactivo(docente.estado),
            }
            for docente in docentes
        ],
    }


def _sheet_carreras(db: Session) -> dict:
    carreras = (
        db.query(Carrera)
        .options(joinedload(Carrera.planes))
        .order_by(Carrera.id_carrera)
        .all()
    )

    return {
        "name": "Carreras",
        "columns": [
            {"key": "id_carrera", "header": "ID carrera"},
            {"key": "clave", "header": "Clave"},
            {"key": "rvoe", "header": "RVOE"},
            {"key": "nombre", "header": "Nombre"},
            {"key": "nivel", "header": "Nivel"},
            {
                "key": "duracion_cuatrimestres",
                "header": "Duracion cuatrimestres"
            },
            {"key": "estado", "header": "Estado"},
            {"key": "planes", "header": "Planes registrados"},
        ],
        "rows": [
            {
                "id_carrera": carrera.id_carrera,
                "clave": carrera.clave,
                "rvoe": carrera.rvoe,
                "nombre": carrera.nombre,
                "nivel": carrera.nivel,
                "duracion_cuatrimestres": carrera.duracion_cuatrimestres,
                "estado": _activo_inactivo(carrera.estado),
                "planes": len(carrera.planes),
            }
            for carrera in carreras
        ],
    }


def _sheet_materias(db: Session) -> dict:
    materias = (
        db.query(Materia)
        .order_by(Materia.id_materia)
        .all()
    )

    return {
        "name": "Materias",
        "columns": [
            {"key": "id_materia", "header": "ID materia"},
            {"key": "clave", "header": "Clave"},
            {"key": "nombre", "header": "Nombre"},
            {"key": "creditos", "header": "Creditos"},
            {"key": "estado", "header": "Estado"},
        ],
        "rows": [
            {
                "id_materia": materia.id_materia,
                "clave": materia.clave,
                "nombre": materia.nombre,
                "creditos": materia.creditos,
                "estado": _activo_inactivo(materia.estado),
            }
            for materia in materias
        ],
    }


def _sheet_planes_estudio(db: Session) -> dict:
    planes = (
        db.query(PlanEstudio)
        .options(
            joinedload(PlanEstudio.carrera),
            joinedload(PlanEstudio.materias)
        )
        .order_by(PlanEstudio.id_plan)
        .all()
    )

    return {
        "name": "Planes",
        "columns": [
            {"key": "id_plan", "header": "ID plan"},
            {"key": "carrera", "header": "Carrera"},
            {"key": "clave_carrera", "header": "Clave carrera"},
            {"key": "nombre_plan", "header": "Nombre plan"},
            {"key": "fecha_inicio", "header": "Fecha inicio"},
            {"key": "fecha_fin", "header": "Fecha fin"},
            {"key": "vigente", "header": "Vigente"},
            {"key": "materias", "header": "Materias registradas"},
        ],
        "rows": [
            {
                "id_plan": plan.id_plan,
                "carrera": plan.carrera.nombre if plan.carrera else "",
                "clave_carrera": plan.carrera.clave if plan.carrera else "",
                "nombre_plan": plan.nombre_plan,
                "fecha_inicio": plan.fecha_inicio,
                "fecha_fin": plan.fecha_fin,
                "vigente": _si_no(plan.vigente),
                "materias": len(plan.materias),
            }
            for plan in planes
        ],
    }


def _sheet_grupos(db: Session) -> dict:
    grupos = (
        db.query(Grupo)
        .options(
            joinedload(Grupo.carrera),
            joinedload(Grupo.cuatrimestre),
            joinedload(Grupo.materias)
        )
        .order_by(Grupo.id_grupo)
        .all()
    )

    return {
        "name": "Grupos",
        "columns": [
            {"key": "id_grupo", "header": "ID grupo"},
            {"key": "nombre", "header": "Nombre"},
            {"key": "carrera", "header": "Carrera"},
            {"key": "cuatrimestre", "header": "Cuatrimestre"},
            {"key": "turno", "header": "Turno"},
            {"key": "materias", "header": "Materias asignadas"},
        ],
        "rows": [
            {
                "id_grupo": grupo.id_grupo,
                "nombre": grupo.nombre,
                "carrera": grupo.carrera.nombre if grupo.carrera else "",
                "cuatrimestre": (
                    grupo.cuatrimestre.nombre if grupo.cuatrimestre else ""
                ),
                "turno": grupo.turno,
                "materias": len(grupo.materias),
            }
            for grupo in grupos
        ],
    }


def _sheet_periodos(db: Session) -> dict:
    periodos = (
        db.query(Periodo)
        .order_by(Periodo.id_periodo)
        .all()
    )

    return {
        "name": "Periodos",
        "columns": [
            {"key": "id_periodo", "header": "ID periodo"},
            {"key": "nombre", "header": "Nombre"},
            {"key": "fecha_inicio", "header": "Fecha inicio"},
            {"key": "fecha_fin", "header": "Fecha fin"},
            {"key": "estado", "header": "Estado"},
        ],
        "rows": [
            {
                "id_periodo": periodo.id_periodo,
                "nombre": periodo.nombre,
                "fecha_inicio": periodo.fecha_inicio,
                "fecha_fin": periodo.fecha_fin,
                "estado": periodo.estado,
            }
            for periodo in periodos
        ],
    }


REPORTES = {
    "alumnos": {
        "nombre": "Alumnos",
        "descripcion": "Datos generales, carrera, plan y estatus escolar.",
        "model": Alumno,
        "builder": _sheet_alumnos,
    },
    "docentes": {
        "nombre": "Docentes",
        "descripcion": "Datos laborales y contacto institucional.",
        "model": Docente,
        "builder": _sheet_docentes,
    },
    "usuarios": {
        "nombre": "Usuarios",
        "descripcion": "Usuarios del sistema con roles asignados.",
        "model": Usuario,
        "builder": _sheet_usuarios,
    },
    "carreras": {
        "nombre": "Carreras",
        "descripcion": "Programas academicos, nivel, duracion y estado.",
        "model": Carrera,
        "builder": _sheet_carreras,
    },
    "materias": {
        "nombre": "Materias",
        "descripcion": "Catalogo de materias con clave y creditos.",
        "model": Materia,
        "builder": _sheet_materias,
    },
    "planes_estudio": {
        "nombre": "Planes de estudio",
        "descripcion": "Planes, vigencia y materias registradas.",
        "model": PlanEstudio,
        "builder": _sheet_planes_estudio,
    },
    "grupos": {
        "nombre": "Grupos",
        "descripcion": "Grupos por carrera, cuatrimestre y turno.",
        "model": Grupo,
        "builder": _sheet_grupos,
    },
    "periodos": {
        "nombre": "Periodos",
        "descripcion": "Periodos escolares con fechas y estado.",
        "model": Periodo,
        "builder": _sheet_periodos,
    },
}


def _catalogo_reportes(db: Session) -> list[dict]:
    return [
        {
            "id": reporte_id,
            "nombre": config["nombre"],
            "descripcion": config["descripcion"],
            "total": db.query(config["model"]).count(),
        }
        for reporte_id, config in REPORTES.items()
    ]


def _excel_response(content: bytes, filename: str) -> Response:
    return Response(
        content=content,
        media_type=EXCEL_MEDIA_TYPE,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


def _calcular_edad(fecha_nacimiento) -> int | None:
    if not fecha_nacimiento:
        return None

    hoy = date.today()
    cumplio_anios = (
        (hoy.month, hoy.day) >=
        (fecha_nacimiento.month, fecha_nacimiento.day)
    )

    return hoy.year - fecha_nacimiento.year - (0 if cumplio_anios else 1)


def _sexo_reinscripcion(sexo: str | None) -> str:
    if sexo == "M":
        return "H"
    if sexo == "F":
        return "M"

    return ""


def _numero_periodo_reinscripcion(periodo: Periodo | None) -> int | None:
    if not periodo or not periodo.fecha_inicio:
        return None

    mes = periodo.fecha_inicio.month

    if mes <= 4:
        return 1
    if mes <= 8:
        return 2

    return 3


def _ciclo_reinscripcion(periodo: Periodo | None) -> str:
    if not periodo or not periodo.fecha_inicio:
        return ""

    numero_periodo = _numero_periodo_reinscripcion(periodo)
    anio = periodo.fecha_inicio.year

    if periodo.fecha_inicio.month >= 9:
        inicio = anio
        fin = anio + 1
    else:
        inicio = anio - 1
        fin = anio

    return f"{inicio} - {fin} - {numero_periodo}"


def _recepciones_por_alumno(db: Session, alumno_ids: list[int]) -> dict[int, RecepcionDocumento]:
    if not alumno_ids:
        return {}

    recepciones = (
        db.query(RecepcionDocumento)
        .filter(RecepcionDocumento.id_alumno.in_(alumno_ids))
        .order_by(
            RecepcionDocumento.id_alumno,
            RecepcionDocumento.fecha_recepcion.desc(),
            RecepcionDocumento.id_recepcion.desc()
        )
        .all()
    )

    resultado = {}

    for recepcion in recepciones:
        if recepcion.id_alumno not in resultado:
            resultado[recepcion.id_alumno] = recepcion

    return resultado


@router.get("/reinscripcion-alumnos")
def obtener_reporte_reinscripcion_alumnos(
    grupo_id: int,
    periodo_id: int | None = None,
    escuela: str = "CENTRO DE ESTUDIOS SUPERIORES DE LA FRONTERA (UNIFRONT)",
    ubicacion: str = "BLVD. BERNARDO O HIGGINS NUMERO 6030 3RA. ETAPA ZONA RIO",
    ciudad: str = "TIJUANA",
    clave: str = "02PSU0015M",
    coordinador_control_escolar: str = "GLENDA LAURA ESCANDON SIQUEIROS",
    control_escolar: str = "VICTOR HUGO BORZANI RODRIGUEZ",
    version: str = "IPES v 1.0.30",
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_reportes_role)
):
    grupo = (
        db.query(Grupo)
        .options(
            joinedload(Grupo.carrera),
            joinedload(Grupo.cuatrimestre)
        )
        .filter(Grupo.id_grupo == grupo_id)
        .first()
    )

    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grupo no encontrado"
        )

    periodo_query = db.query(Periodo)

    if periodo_id is not None:
        periodo = (
            periodo_query
            .filter(Periodo.id_periodo == periodo_id)
            .first()
        )
    else:
        periodo = (
            periodo_query
            .filter(Periodo.estado == "ACTIVO")
            .order_by(Periodo.fecha_inicio.desc())
            .first()
        )

    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Periodo no encontrado"
        )

    inscripciones_query = (
        db.query(Inscripcion)
        .join(Inscripcion.alumno)
        .join(Alumno.usuario)
        .options(
            joinedload(Inscripcion.alumno).joinedload(Alumno.usuario),
            joinedload(Inscripcion.alumno).joinedload(Alumno.carrera),
            joinedload(Inscripcion.grupo).joinedload(Grupo.carrera),
            joinedload(Inscripcion.grupo).joinedload(Grupo.cuatrimestre),
            joinedload(Inscripcion.periodo)
        )
        .filter(
            Inscripcion.id_grupo == grupo_id,
            Inscripcion.id_periodo == periodo.id_periodo,
            Inscripcion.estado == "ACTIVO"
        )
        .order_by(
            Usuario.apellido_paterno,
            Usuario.apellido_materno,
            Usuario.nombre
        )
    )

    inscripciones = inscripciones_query.all()
    alumno_ids = [
        inscripcion.id_alumno
        for inscripcion in inscripciones
        if inscripcion.id_alumno is not None
    ]
    recepciones = _recepciones_por_alumno(db, alumno_ids)

    alumnos = []

    for index, inscripcion in enumerate(inscripciones, start=1):
        alumno = inscripcion.alumno
        recepcion = recepciones.get(alumno.id_alumno) if alumno else None

        alumnos.append({
            "no": index,
            "id_alumno": alumno.id_alumno if alumno else None,
            "matricula": alumno.matricula if alumno else "",
            "nombre": _nombre_usuario(alumno.usuario).upper() if alumno else "",
            "edad": _calcular_edad(alumno.fecha_nacimiento) if alumno else None,
            "sexo": _sexo_reinscripcion(alumno.sexo) if alumno else "",
            "sexo_origen": alumno.sexo if alumno else "",
            "a_nac": _marca(recepcion.acta_original if recepcion else False),
            "c_est": _marca(
                (
                    recepcion.certificado_original or
                    recepcion.constancia_terminacion
                )
                if recepcion else False
            ),
            "observaciones": recepcion.observaciones if recepcion else "",
            "numero_control": alumno.numero_control if alumno else "",
            "fecha_validacion": (
                recepcion.fecha_recepcion
                if recepcion and recepcion.fecha_recepcion
                else inscripcion.fecha_inscripcion
            )
        })

    carrera = grupo.carrera
    cuatrimestre = grupo.cuatrimestre

    return {
        "titulo": "Registro de Reinscripcion de Alumnos",
        "encabezado": {
            "dependencia": "Secretaria de Educacion",
            "subsecretaria": (
                "Subsecretaria de Educacion Media Superior, "
                "Superior e Investigacion"
            ),
            "escuela": escuela,
            "ubicacion": ubicacion,
            "ciudad": ciudad,
            "carrera": carrera.nombre if carrera else "",
            "cuatrimestre": (
                cuatrimestre.nombre.upper()
                if cuatrimestre else ""
            ),
            "grupo": grupo.nombre,
            "clave": clave,
            "rvoe": carrera.rvoe if carrera else "",
            "ciclo": _ciclo_reinscripcion(periodo),
            "periodo": {
                "id_periodo": periodo.id_periodo,
                "nombre": periodo.nombre,
                "fecha_inicio": periodo.fecha_inicio,
                "fecha_fin": periodo.fecha_fin,
                "estado": periodo.estado
            }
        },
        "columnas": [
            {"key": "no", "label": "No."},
            {"key": "nombre", "label": "Nombre"},
            {"key": "edad", "label": "Edad"},
            {"key": "sexo", "label": "Sexo"},
            {"key": "a_nac", "label": "A.Nac."},
            {"key": "c_est", "label": "C.Est"},
            {"key": "observaciones", "label": "Observaciones"},
            {"key": "numero_control", "label": "No.Control"},
            {"key": "fecha_validacion", "label": "Fec.Validacion"}
        ],
        "alumnos": alumnos,
        "firmas": {
            "coordinador_control_escolar": coordinador_control_escolar,
            "control_escolar": control_escolar
        },
        "pie": {
            "version": version,
            "fecha": date.today(),
            "pagina": 1,
            "total_paginas": 1
        }
    }


@router.get("")
@router.get("/")
def listar_reportes_fundamentales(
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_reportes_role)
):
    return _catalogo_reportes(db)


@router.get("/excel")
def exportar_reportes_fundamentales(
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_reportes_role)
):
    sheets = [config["builder"](db) for config in REPORTES.values()]
    content = build_xlsx(sheets, title="Reportes fundamentales")

    return _excel_response(content, "reportes_fundamentales.xlsx")


@router.get("/{reporte_id}/excel")
def exportar_reporte_fundamental(
    reporte_id: str,
    db: Session = Depends(get_db),
    _: Usuario = Depends(_require_reportes_role)
):
    config = REPORTES.get(reporte_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado"
        )

    content = build_xlsx(
        [config["builder"](db)],
        title=f"Reporte {config['nombre']}"
    )

    return _excel_response(content, f"reporte_{reporte_id}.xlsx")
