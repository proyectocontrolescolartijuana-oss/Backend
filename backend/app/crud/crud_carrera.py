from sqlalchemy.orm import Session
from app.models.carrera import Carrera
from app.schemas.carrera import CarreraCreate

def get_carreras(db: Session):
    return db.query(Carrera).all()

def get_carrera(db: Session, carrera_id: int):
    return (
        db.query(Carrera)
        .filter(Carrera.id_carrera == carrera_id)
        .first()
    )

def create_carrera(
    db: Session,
    carrera: CarreraCreate
):
    nueva_carrera = Carrera(
        **carrera.model_dump()
    )

    db.add(nueva_carrera)
    db.commit()
    db.refresh(nueva_carrera)

    return nueva_carrera

def update_carrera(
    db: Session,
    carrera_id: int,
    carrera_data
):
    carrera = get_carrera(db, carrera_id)

    if not carrera:
        return None

    update_data = carrera_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(carrera, key, value)

    db.commit()
    db.refresh(carrera)

    return carrera

def delete_carrera(
    db: Session,
    carrera_id: int
):
    carrera = get_carrera(db, carrera_id)

    if not carrera:
        return False

    db.delete(carrera)
    db.commit()

    return True
