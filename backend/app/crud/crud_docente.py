from sqlalchemy.orm import Session

from app.models.docente import Docente

from app.schemas.docente import DocenteCreate

def get_docentes(db: Session):
    return db.query(Docente).all()

def get_docente(db: Session, docente_id: int):
    return (
        db.query(Docente)
        .filter(Docente.id_docente == docente_id)
        .first()
    )

def create_docente(
    db: Session,
    docente: DocenteCreate
):
    nuevo_docente = Docente(
        **docente.model_dump()
    )

    db.add(nuevo_docente)

    db.commit()

    db.refresh(nuevo_docente)

    return nuevo_docente

def update_docente(
    db: Session,
    docente_id: int,
    docente_data
):
    docente = get_docente(db, docente_id)

    if not docente:
        return None

    update_data = docente_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(docente, key, value)

    db.commit()
    db.refresh(docente)

    return docente

def delete_docente(
    db: Session,
    docente_id: int
):
    docente = get_docente(db, docente_id)

    if not docente:
        return False

    db.delete(docente)
    db.commit()

    return True
