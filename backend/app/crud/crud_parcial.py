from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.asistencia import Asistencia
from app.models.calificacion import Calificacion
from app.models.desglose import DesgloseCriterio
from app.models.parcial import Parcial

from app.schemas.parcial import ParcialCreate


def _tiene_informacion(db: Session, parcial_id: int) -> bool:
    """True si el parcial ya tiene calificaciones, asistencias o desglose."""
    return any(
        db.query(modelo.id_parcial)
        .filter(modelo.id_parcial == parcial_id)
        .first()
        is not None
        for modelo in (Calificacion, Asistencia, DesgloseCriterio)
    )


def get_parciales(db: Session, modalidad: Optional[str] = None):
    query = db.query(Parcial)

    if modalidad:
        query = query.filter(Parcial.modalidad == modalidad)

    return query.order_by(Parcial.id_parcial).all()

def get_parcial(db: Session, parcial_id: int):
    return (
        db.query(Parcial)
        .filter(Parcial.id_parcial == parcial_id)
        .first()
    )

def create_parcial(
    db: Session,
    parcial: ParcialCreate
):
    nuevo_parcial = Parcial(
        **parcial.model_dump()
    )

    db.add(nuevo_parcial)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "Ya existe un parcial con ese nombre en la modalidad indicada"
        ) from error

    db.refresh(nuevo_parcial)

    return nuevo_parcial

def update_parcial(
    db: Session,
    parcial_id: int,
    parcial_data
):
    parcial = get_parcial(db, parcial_id)

    if not parcial:
        return None

    update_data = parcial_data.model_dump(
        exclude_unset=True
    )

    cambia_modalidad = (
        "modalidad" in update_data
        and update_data["modalidad"] != parcial.modalidad
    )

    if cambia_modalidad and _tiene_informacion(db, parcial_id):
        raise ValueError(
            "No se puede cambiar la modalidad de un parcial que ya tiene "
            "calificaciones, asistencias o desglose"
        )

    for key, value in update_data.items():
        setattr(parcial, key, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "Ya existe un parcial con ese nombre en la modalidad indicada"
        ) from error

    db.refresh(parcial)

    return parcial

def delete_parcial(
    db: Session,
    parcial_id: int
):
    parcial = get_parcial(db, parcial_id)

    if not parcial:
        return False

    if _tiene_informacion(db, parcial_id):
        raise ValueError(
            "No se puede eliminar el parcial porque ya tiene calificaciones, "
            "asistencias o desglose"
        )

    db.delete(parcial)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "No se puede eliminar el parcial porque tiene informacion "
            "relacionada"
        ) from error

    return True