from sqlalchemy.orm import Session

from app.models.calificacion import Calificacion

from app.schemas.calificacion import (
    CalificacionCreate
)

def get_calificaciones(db: Session):
    return db.query(Calificacion).all()

def get_calificacion(db: Session, calificacion_id: int):
    return (
        db.query(Calificacion)
        .filter(Calificacion.id_calificacion == calificacion_id)
        .first()
    )

def create_calificacion(
    db: Session,
    calificacion: CalificacionCreate
):
    nueva_calificacion = Calificacion(
        **calificacion.model_dump()
    )

    db.add(nueva_calificacion)

    db.commit()

    db.refresh(nueva_calificacion)

    return nueva_calificacion

def update_calificacion(
    db: Session,
    calificacion_id: int,
    calificacion_data
):
    calificacion = get_calificacion(db, calificacion_id)

    if not calificacion:
        return None

    update_data = calificacion_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(calificacion, key, value)

    db.commit()
    db.refresh(calificacion)

    return calificacion

def delete_calificacion(
    db: Session,
    calificacion_id: int
):
    calificacion = get_calificacion(db, calificacion_id)

    if not calificacion:
        return False

    db.delete(calificacion)
    db.commit()

    return True
