from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.alumno import Alumno
from app.models.carga_academica import CargaAcademica
from app.models.grupo import Grupo
from app.models.grupo_materia import GrupoMateria
from app.models.historial_academico import HistorialAcademico
from app.models.plan_materia import PlanMateria
from app.models.usuario import Usuario


def _split_nombre(apellido_paterno: str | None, apellido_materno: str | None):
    return apellido_paterno or "", apellido_materno or ""


def _nombre_completo(usuario):
    if not usuario:
        return ""

    return " ".join(
        part
        for part in (
            usuario.nombre,
            usuario.apellido_paterno,
            usuario.apellido_materno,
        )
        if part
    )


def buscar_alumnos_kardex(db: Session, query: str, limit: int = 8):
    query = (query or "").strip()

    if len(query) < 2:
        return []

    like = f"%{query.lower()}%"
    nombre_completo = func.lower(
        func.concat(
            Usuario.nombre,
            " ",
            Usuario.apellido_paterno,
            " ",
            func.coalesce(Usuario.apellido_materno, ""),
        )
    )

    alumnos = (
        db.query(Alumno)
        .join(Alumno.usuario)
        .options(joinedload(Alumno.usuario), joinedload(Alumno.carrera))
        .filter(
            or_(
                func.lower(Alumno.matricula).like(like),
                nombre_completo.like(like),
            )
        )
        .order_by(Alumno.matricula.asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id_alumno": alumno.id_alumno,
            "matricula": alumno.matricula or "",
            "nombre": _nombre_completo(alumno.usuario),
            "carrera": alumno.carrera.nombre if alumno.carrera else "",
        }
        for alumno in alumnos
    ]


def get_kardex_by_matricula(db: Session, matricula: str):
    alumno = (
        db.query(Alumno)
        .options(
            joinedload(Alumno.usuario),
            joinedload(Alumno.carrera),
            joinedload(Alumno.plan),
        )
        .filter(Alumno.matricula == matricula)
        .first()
    )

    if not alumno:
        return None

    usuario = alumno.usuario

    primer_apellido, segundo_apellido = _split_nombre(
        getattr(usuario, "apellido_paterno", None),
        getattr(usuario, "apellido_materno", None),
    )

    cargas = (
        db.query(CargaAcademica)
        .options(
            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.grupo)
            .joinedload(Grupo.cuatrimestre),

            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.materia),

            joinedload(CargaAcademica.grupo_materia)
            .joinedload(GrupoMateria.periodo),
        )
        .filter(CargaAcademica.id_alumno == alumno.id_alumno)
        .all()
    )

    historial_map = defaultdict(list)

    ids_materias = [
        c.grupo_materia.id_materia
        for c in cargas
        if c.grupo_materia and c.grupo_materia.materia
    ]

    ids_periodos = [
        c.grupo_materia.id_periodo
        for c in cargas
        if c.grupo_materia and c.grupo_materia.periodo
    ]

    historial_rows = (
        db.query(HistorialAcademico)
        .filter(
            HistorialAcademico.id_alumno == alumno.id_alumno,
            HistorialAcademico.id_materia.in_(ids_materias) if ids_materias else False,
            HistorialAcademico.id_periodo.in_(ids_periodos) if ids_periodos else False,
        )
        .all()
    )

    historial_lookup = {}

    for h in historial_rows:
        if h.calificacion_final is None:
            continue

        historial_lookup[
            (h.id_materia, h.id_periodo)
        ] = float(h.calificacion_final)

    plan_materias = (
        db.query(PlanMateria)
        .filter(
            PlanMateria.id_plan == alumno.id_plan,
            PlanMateria.id_materia.in_(ids_materias) if ids_materias else False,
        )
        .all()
    )
    cuatrimestre_por_materia = {
        pm.id_materia: pm.cuatrimestre.numero
        for pm in plan_materias
        if pm.cuatrimestre
    }

    for carga in cargas:
        gm = carga.grupo_materia

        if not gm:
            continue

        if not gm.grupo:
            continue

        if not gm.materia:
            continue

        if not gm.periodo:
            continue

        cuatrimestre_num = cuatrimestre_por_materia.get(gm.id_materia, 0)

        if not cuatrimestre_num and gm.grupo.cuatrimestre:
            cuatrimestre_num = gm.grupo.cuatrimestre.numero

        periodo_escolar = gm.periodo.nombre or ""
        grupo_nombre = gm.grupo.nombre or ""

        calificacion_final = historial_lookup.get(
            (gm.id_materia, gm.id_periodo),
            0.0
        )

        historial_map[
            (
                cuatrimestre_num,
                periodo_escolar,
                grupo_nombre
            )
        ].append(
            {
                "clave": gm.materia.clave or "",
                "asignatura": gm.materia.nombre or "",
                "creditos": float(gm.materia.creditos or 0),
                "calificacion_final": float(calificacion_final),
            }
        )

    historial = []

    for (
        cuatrimestre_num,
        periodo_escolar,
        grupo_nombre,
    ) in sorted(
        historial_map.keys(),
        key=lambda x: (x[0], x[1], x[2]),
    ):
        historial.append(
            {
                "cuatrimestre": cuatrimestre_num,
                "periodo_escolar": periodo_escolar,
                "grupo": grupo_nombre,
                "materias": historial_map[
                    (
                        cuatrimestre_num,
                        periodo_escolar,
                        grupo_nombre,
                    )
                ],
            }
        )

    return {
        "matricula": alumno.matricula or "",
        "primer_apellido": primer_apellido,
        "segundo_apellido": segundo_apellido,
        "nombre": getattr(usuario, "nombre", "") if usuario else "",
        "carrera": alumno.carrera.nombre if alumno.carrera else "",
        "logo": alumno.carrera.logo if alumno.carrera else None,
        "plan_estudios": (
            alumno.plan.nombre_plan
            if alumno.plan
            else ""
        ),
        "historial": historial,
    }


def get_kardex_by_query(db: Session, query: str):
    query = (query or "").strip()

    if not query:
        return None

    alumno = (
        db.query(Alumno)
        .join(Alumno.usuario)
        .filter(Alumno.matricula == query)
        .first()
    )

    if not alumno:
        like = f"%{query.lower()}%"
        nombre_completo = func.lower(
            func.concat(
                Usuario.nombre,
                " ",
                Usuario.apellido_paterno,
                " ",
                func.coalesce(Usuario.apellido_materno, ""),
            )
        )

        alumno = (
            db.query(Alumno)
            .join(Alumno.usuario)
            .filter(nombre_completo.like(like))
            .order_by(Alumno.matricula.asc())
            .first()
        )

    if not alumno:
        return None

    return get_kardex_by_matricula(db, alumno.matricula)
