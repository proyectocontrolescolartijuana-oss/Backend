from sqlalchemy.orm import Session

from app.models.titulacion import Titulacion

from app.schemas.titulacion import (
    TitulacionCreate
)

def get_titulaciones(db: Session):
    return db.query(Titulacion).all()

def get_titulacion(db: Session, titulacion_id: int):
    return (
        db.query(Titulacion)
        .filter(Titulacion.id_titulacion == titulacion_id)
        .first()
    )

def create_titulacion(
    db: Session,
    titulacion: TitulacionCreate
):
    nueva_titulacion = Titulacion(
        **titulacion.model_dump()
    )

    db.add(nueva_titulacion)

    db.commit()

    db.refresh(nueva_titulacion)

    return nueva_titulacion

def update_titulacion(
    db: Session,
    titulacion_id: int,
    titulacion_data
):
    titulacion = get_titulacion(db, titulacion_id)

    if not titulacion:
        return None

    update_data = titulacion_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(titulacion, key, value)

    db.commit()
    db.refresh(titulacion)

    return titulacion

def delete_titulacion(
    db: Session,
    titulacion_id: int
):
    titulacion = get_titulacion(db, titulacion_id)

    if not titulacion:
        return False

    db.delete(titulacion)
    db.commit()

    return True
