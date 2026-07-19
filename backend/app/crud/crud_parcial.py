from sqlalchemy.orm import Session

from app.models.parcial import Parcial

from app.schemas.parcial import ParcialCreate

def get_parciales(db: Session):
    return db.query(Parcial).all()

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

    db.commit()

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

    for key, value in update_data.items():
        setattr(parcial, key, value)

    db.commit()
    db.refresh(parcial)

    return parcial

def delete_parcial(
    db: Session,
    parcial_id: int
):
    parcial = get_parcial(db, parcial_id)

    if not parcial:
        return False

    db.delete(parcial)
    db.commit()

    return True
