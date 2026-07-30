from sqlalchemy.orm import Session

from app.models.periodo import Periodo

from app.schemas.periodo import PeriodoCreate

def get_periodos(db: Session):
    return db.query(Periodo).all()

def get_periodo(db: Session, periodo_id: int):
    return (
        db.query(Periodo)
        .filter(Periodo.id_periodo == periodo_id)
        .first()
    )

def existe_periodo_activo(db: Session, excluir_periodo_id: int | None = None):
    query = db.query(Periodo).filter(Periodo.estado == "ACTIVO")

    if excluir_periodo_id is not None:
        query = query.filter(Periodo.id_periodo != excluir_periodo_id)

    return query.first() is not None

def marcar_otros_periodos_como_pendientes(db: Session, periodo_id: int):
    (
        db.query(Periodo)
        .filter(
            Periodo.estado == "ACTIVO",
            Periodo.id_periodo != periodo_id
        )
        .update(
            {Periodo.estado: "PENDIENTE"},
            synchronize_session=False
        )
    )

def create_periodo(
    db: Session,
    periodo: PeriodoCreate
):
    periodo_data = periodo.model_dump()

    if existe_periodo_activo(db):
        periodo_data["estado"] = "PENDIENTE"
    else:
        periodo_data["estado"] = periodo_data.get("estado") or "ACTIVO"

    nuevo_periodo = Periodo(
        **periodo_data
    )

    db.add(nuevo_periodo)

    db.commit()

    db.refresh(nuevo_periodo)

    return nuevo_periodo

def update_periodo(
    db: Session,
    periodo_id: int,
    periodo_data
):
    periodo = get_periodo(db, periodo_id)

    if not periodo:
        return None

    update_data = periodo_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(periodo, key, value)

    db.commit()
    db.refresh(periodo)

    return periodo

def delete_periodo(
    db: Session,
    periodo_id: int
):
    periodo = get_periodo(db, periodo_id)

    if not periodo:
        return False

    db.delete(periodo)
    db.commit()

    return True
