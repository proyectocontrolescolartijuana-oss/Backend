from datetime import date

from sqlalchemy.orm import Session

from app.crud._crud_utils import to_create_data, to_update_data
from app.models.alumno import Alumno
from app.models.historial_academico import HistorialAcademico
from app.models.periodo import Periodo
from app.models.plan_materia import PlanMateria

CALIFICACION_APROBATORIA_EQUIVALENCIA = 70


def get_historiales_academicos(db: Session):
    return db.query(HistorialAcademico).all()


def get_historial_academico(db: Session, historial_id: int):
    return (
        db.query(HistorialAcademico)
        .filter(HistorialAcademico.id_historial == historial_id)
        .first()
    )


def create_historial_academico(db: Session, historial_data):
    nuevo_historial = HistorialAcademico(**to_create_data(historial_data))

    db.add(nuevo_historial)
    db.commit()
    db.refresh(nuevo_historial)

    return nuevo_historial


def registrar_equivalencias(db: Session, alumno_id: int, equivalencias_data):
    alumno = (
        db.query(Alumno)
        .filter(Alumno.id_alumno == alumno_id)
        .first()
    )

    if not alumno:
        raise ValueError("Alumno no encontrado")

    data = equivalencias_data.model_dump()

    periodo = (
        db.query(Periodo.id_periodo)
        .filter(Periodo.id_periodo == data["id_periodo"])
        .first()
    )

    if not periodo:
        raise ValueError("Periodo no encontrado")

    materias_data = data.get("materias") or []

    if not materias_data:
        raise ValueError("Debe capturar al menos una materia por equivalencia")

    ids_materias_plan = {
        id_materia
        for (id_materia,) in (
            db.query(PlanMateria.id_materia)
            .filter(PlanMateria.id_plan == alumno.id_plan)
            .all()
        )
    }

    fecha_cierre = data.get("fecha_cierre") or date.today()
    registros = []

    for materia_data in materias_data:
        id_materia = materia_data["id_materia"]
        calificacion_final = float(materia_data["calificacion_final"])

        if id_materia not in ids_materias_plan:
            raise ValueError("La materia no pertenece al plan del alumno")

        if calificacion_final < 0 or calificacion_final > 100:
            raise ValueError(
                "La calificacion por equivalencia debe estar entre 0 y 100"
            )

        resultado = (
            "APROBADO"
            if calificacion_final >= CALIFICACION_APROBATORIA_EQUIVALENCIA
            else "REPROBADO"
        )
        historial_existente = (
            db.query(HistorialAcademico)
            .filter(
                HistorialAcademico.id_alumno == alumno_id,
                HistorialAcademico.id_materia == id_materia,
            )
            .order_by(HistorialAcademico.id_historial.desc())
            .first()
        )

        datos_historial = {
            "id_alumno": alumno_id,
            "id_materia": id_materia,
            "id_periodo": data["id_periodo"],
            "tipo_evaluacion": "EQUIVALENCIA",
            "oportunidad": 1,
            "calificacion_final": calificacion_final,
            "resultado": resultado,
            "fecha_cierre": fecha_cierre,
        }

        if historial_existente:
            if historial_existente.tipo_evaluacion != "EQUIVALENCIA":
                raise ValueError(
                    "La materia ya tiene historial academico registrado"
                )

            for key, value in datos_historial.items():
                setattr(historial_existente, key, value)

            registros.append(historial_existente)
            continue

        nuevo_historial = HistorialAcademico(**datos_historial)
        db.add(nuevo_historial)
        registros.append(nuevo_historial)

    db.commit()

    for registro in registros:
        db.refresh(registro)

    return registros


def update_historial_academico(db: Session, historial_id: int, historial_data):
    historial = get_historial_academico(db, historial_id)

    if not historial:
        return None

    for key, value in to_update_data(historial_data).items():
        setattr(historial, key, value)

    db.commit()
    db.refresh(historial)

    return historial


def delete_historial_academico(db: Session, historial_id: int):
    historial = get_historial_academico(db, historial_id)

    if not historial:
        return False

    db.delete(historial)
    db.commit()

    return True
