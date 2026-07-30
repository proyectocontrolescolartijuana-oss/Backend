from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.carrera import Carrera
from app.schemas.carrera import CarreraCreate

LOGOS_DIR = Path(__file__).resolve().parents[1] / "static" / "logos"


def _nombre_logo_local(logo: str | None):
    if not logo:
        return None

    if logo.startswith("http://localhost:8000/static/logos/"):
        return logo.rsplit("/", 1)[-1]

    if logo.startswith("/static/logos/"):
        return logo.rsplit("/", 1)[-1]

    if logo.startswith(("http://", "https://")):
        return None

    return Path(logo).name


def _logo_en_uso(db: Session, logo: str, excluir_carrera_id: int | None = None):
    query = db.query(Carrera.id_carrera).filter(Carrera.logo == logo)

    if excluir_carrera_id is not None:
        query = query.filter(Carrera.id_carrera != excluir_carrera_id)

    return query.first() is not None


def _eliminar_logo_si_no_esta_en_uso(
    db: Session,
    logo: str | None,
    excluir_carrera_id: int | None = None
):
    nombre_logo = _nombre_logo_local(logo)

    if not nombre_logo:
        return

    if _logo_en_uso(db, logo, excluir_carrera_id):
        return

    archivo = (LOGOS_DIR / nombre_logo).resolve()

    try:
        archivo.relative_to(LOGOS_DIR.resolve())
    except ValueError:
        return

    if archivo.is_file():
        archivo.unlink()


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

    logo_anterior = carrera.logo
    update_data = carrera_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(carrera, key, value)

    db.commit()
    db.refresh(carrera)

    if "logo" in update_data and update_data["logo"] != logo_anterior:
        _eliminar_logo_si_no_esta_en_uso(
            db,
            logo_anterior,
            excluir_carrera_id=carrera_id
        )

    return carrera

def delete_carrera(
    db: Session,
    carrera_id: int
):
    carrera = get_carrera(db, carrera_id)

    if not carrera:
        return False

    logo_anterior = carrera.logo

    db.delete(carrera)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError(
            "No se puede eliminar la carrera porque tiene informacion relacionada"
        ) from error

    _eliminar_logo_si_no_esta_en_uso(db, logo_anterior)

    return True
