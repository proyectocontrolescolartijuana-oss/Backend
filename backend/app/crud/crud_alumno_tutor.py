from sqlalchemy import and_, delete, insert, select
from sqlalchemy.orm import Session

from app.models.alumno_tutor import alumno_tutor


def get_alumnos_tutores(db: Session):
    return db.execute(select(alumno_tutor)).mappings().all()


def get_alumno_tutor(db: Session, alumno_id: int, tutor_id: int):
    return (
        db.execute(
            select(alumno_tutor).where(
                and_(
                    alumno_tutor.c.id_alumno == alumno_id,
                    alumno_tutor.c.id_tutor == tutor_id
                )
            )
        )
        .mappings()
        .first()
    )


def create_alumno_tutor(db: Session, alumno_id: int, tutor_id: int):
    relacion = get_alumno_tutor(db, alumno_id, tutor_id)

    if relacion:
        return relacion

    db.execute(
        insert(alumno_tutor).values(
            id_alumno=alumno_id,
            id_tutor=tutor_id
        )
    )
    db.commit()

    return get_alumno_tutor(db, alumno_id, tutor_id)


def delete_alumno_tutor(db: Session, alumno_id: int, tutor_id: int):
    result = db.execute(
        delete(alumno_tutor).where(
            and_(
                alumno_tutor.c.id_alumno == alumno_id,
                alumno_tutor.c.id_tutor == tutor_id
            )
        )
    )
    db.commit()

    return result.rowcount > 0
