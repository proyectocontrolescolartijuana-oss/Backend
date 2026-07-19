from sqlalchemy.orm import Session

from app.models.materia import Materia
from app.schemas.materia import MateriaCreate

def get_materias(db: Session):
    return db.query(Materia).all()

def get_materia(db: Session, materia_id: int):
    return (
        db.query(Materia)
        .filter(Materia.id_materia == materia_id)
        .first()
    )

def create_materia(
    db: Session,
    materia: MateriaCreate
):
    nueva_materia = Materia(
        **materia.model_dump()
    )

    db.add(nueva_materia)
    db.commit()
    db.refresh(nueva_materia)

    return nueva_materia

def update_materia(
    db: Session,
    materia_id: int,
    materia_data
):
    materia = get_materia(db, materia_id)

    if not materia:
        return None

    update_data = materia_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(materia, key, value)

    db.commit()
    db.refresh(materia)

    return materia

def delete_materia(
    db: Session,
    materia_id: int
):
    materia = get_materia(db, materia_id)

    if not materia:
        return False

    db.delete(materia)
    db.commit()

    return True
