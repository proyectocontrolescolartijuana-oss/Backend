from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.cuatrimestre import Cuatrimestre
from app.models.grupo import Grupo
from app.models.grupo_materia import GrupoMateria

from app.schemas.periodo import (
    PeriodoCreate,
    PeriodoResponse,
    PeriodoUpdate
)

from app.crud.crud_periodo import (
    get_periodos,
    get_periodo,
    create_periodo,
    update_periodo,
    delete_periodo
)

router = APIRouter(
    prefix="/periodos",
    tags=["Periodos"]
)


def progresar_grupos_del_periodo(
    db: Session,
    periodo_id: int
):
    grupos = (
        db.query(Grupo)
        .join(GrupoMateria, GrupoMateria.id_grupo == Grupo.id_grupo)
        .options(
            joinedload(Grupo.carrera),
            joinedload(Grupo.cuatrimestre)
        )
        .filter(GrupoMateria.id_periodo == periodo_id)
        .distinct()
        .all()
    )

    cuatrimestres = db.query(Cuatrimestre).all()
    cuatrimestres_por_numero = {
        cuatrimestre.numero: cuatrimestre
        for cuatrimestre in cuatrimestres
    }

    for grupo in grupos:
        if not grupo.carrera or not grupo.cuatrimestre:
            continue

        numero_actual = grupo.cuatrimestre.numero
        ultimo_cuatrimestre = grupo.carrera.duracion_cuatrimestres

        if numero_actual >= ultimo_cuatrimestre:
            continue

        siguiente_cuatrimestre = cuatrimestres_por_numero.get(
            numero_actual + 1
        )

        if not siguiente_cuatrimestre:
            continue

        grupo.id_cuatrimestre = siguiente_cuatrimestre.id_cuatrimestre

    db.commit()


@router.get(
    "/",
    response_model=list[PeriodoResponse]
)
def listar_periodos(
    db: Session = Depends(get_db)
):
    return get_periodos(db)

@router.get(
    "/{periodo_id}",
    response_model=PeriodoResponse
)
def obtener_periodo(
    periodo_id: int,
    db: Session = Depends(get_db)
):
    periodo = get_periodo(db, periodo_id)

    if not periodo:
        raise HTTPException(
            status_code=404,
            detail="Periodo no encontrado"
        )

    return periodo

@router.post(
    "/",
    response_model=PeriodoResponse
)
def crear_periodo(
    periodo: PeriodoCreate,
    db: Session = Depends(get_db)
):
    return create_periodo(
        db,
        periodo
    )

@router.patch(
    "/{periodo_id}",
    response_model=PeriodoResponse
)
def actualizar_periodo(
    periodo_id: int,
    periodo: PeriodoUpdate,
    db: Session = Depends(get_db)
):
    periodo_actual = get_periodo(db, periodo_id)

    if not periodo_actual:
        raise HTTPException(
            status_code=404,
            detail="Periodo no encontrado"
        )

    cerrar_periodo = (
        periodo_actual.estado != "CERRADO" and
        periodo.estado == "CERRADO"
    )

    periodo_actualizado = update_periodo(
        db,
        periodo_id,
        periodo
    )

    if not periodo_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Periodo no encontrado"
        )

    if cerrar_periodo:
        progresar_grupos_del_periodo(db, periodo_id)
        periodo_actualizado = get_periodo(db, periodo_id)

    return periodo_actualizado

@router.delete(
    "/{periodo_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_periodo(
    periodo_id: int,
    db: Session = Depends(get_db)
):
    eliminado = delete_periodo(db, periodo_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Periodo no encontrado"
        )
