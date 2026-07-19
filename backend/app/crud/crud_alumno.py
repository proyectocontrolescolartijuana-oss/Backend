from datetime import date

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.alumno import Alumno
from app.models.inscripcion import Inscripcion
from app.models.periodo import Periodo

from app.schemas.alumno import AlumnoCreate

MAX_INTENTOS_MATRICULA = 3


def _prefijo_matricula_actual():
    return f"{date.today().year % 100:02d}"


def _calcular_siguiente_matricula(db: Session, bloquear: bool = False):
    prefijo = _prefijo_matricula_actual()

    query = db.query(Alumno.matricula).filter(
        Alumno.matricula.like(f"{prefijo}%")
    )

    if bloquear:
        query = query.with_for_update()

    consecutivos = []

    for (matricula,) in query.all():
        matricula_texto = str(matricula or "")
        consecutivo = matricula_texto[2:]

        if (
            len(matricula_texto) == 6
            and matricula_texto.startswith(prefijo)
            and consecutivo.isdigit()
        ):
            consecutivos.append(int(consecutivo))

    siguiente = max(consecutivos, default=0) + 1

    if siguiente > 9999:
        raise ValueError(
            "Se agotaron las matriculas disponibles para el anio actual"
        )

    return f"{prefijo}{siguiente:04d}"


def get_siguiente_matricula(db: Session):
    return _calcular_siguiente_matricula(db)


def _get_periodo_activo_id(db: Session):
    periodo = (
        db.query(Periodo)
        .filter(Periodo.estado == "ACTIVO")
        .order_by(Periodo.fecha_inicio.desc(), Periodo.id_periodo.desc())
        .first()
    )

    return periodo.id_periodo if periodo else None


def get_alumnos(db: Session):
    return db.query(Alumno).all()

def get_alumno(
    db: Session,
    alumno_id: int
):
    return (
        db.query(Alumno)
        .filter(
            Alumno.id_alumno == alumno_id
        )
        .first()
    )

def create_alumno(
    db: Session,
    alumno: AlumnoCreate
):
    alumno_data = alumno.model_dump()
    id_grupo = alumno_data.pop("id_grupo", None)
    id_periodo = alumno_data.pop("id_periodo", None)
    matricula = str(alumno_data.get("matricula") or "").strip()
    generar_matricula = not matricula

    if matricula:
        alumno_data["matricula"] = matricula
    else:
        alumno_data.pop("matricula", None)

    for intento in range(MAX_INTENTOS_MATRICULA if generar_matricula else 1):
        try:
            if generar_matricula:
                alumno_data["matricula"] = _calcular_siguiente_matricula(
                    db,
                    bloquear=True
                )

            nuevo_alumno = Alumno(**alumno_data)

            db.add(nuevo_alumno)
            db.flush()

            if id_grupo:
                id_periodo_inscripcion = id_periodo or _get_periodo_activo_id(db)

                if not id_periodo_inscripcion:
                    raise ValueError(
                        "Selecciona un periodo para inscribir al alumno"
                    )

                db.add(
                    Inscripcion(
                        id_alumno=nuevo_alumno.id_alumno,
                        id_grupo=id_grupo,
                        id_periodo=id_periodo_inscripcion,
                        fecha_inscripcion=(
                            alumno_data.get("fecha_ingreso") or date.today()
                        ),
                        estado="ACTIVO"
                    )
                )

            db.commit()
            db.refresh(nuevo_alumno)

            return nuevo_alumno
        except IntegrityError:
            db.rollback()

            if not generar_matricula or intento == MAX_INTENTOS_MATRICULA - 1:
                raise

            alumno_data.pop("matricula", None)
        except ValueError:
            db.rollback()
            raise

    raise ValueError("No se pudo generar una matricula disponible")

def get_alumno_by_id(
    db: Session,
    alumno_id: int
):
    return get_alumno(db, alumno_id)


def update_alumno(
    db: Session,
    alumno_id: int,
    alumno_data
):

    alumno = (
        db.query(Alumno)
        .filter(Alumno.id_alumno == alumno_id)
        .first()
    )

    if not alumno:
        return None

    update_data = alumno_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(alumno, key, value)

    db.commit()
    db.refresh(alumno)

    return alumno

def delete_alumno(
    db: Session,
    alumno_id: int
):
    alumno = get_alumno(db, alumno_id)

    if not alumno:
        return False

    db.delete(alumno)
    db.commit()

    return True
