from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from app.database import get_db

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
    delete_periodo,
    marcar_otros_periodos_como_pendientes
)
from app.services.cierre_periodo_service import (
    cerrar_periodo_completo,
    previsualizar_cierre_periodo
)

router = APIRouter(
    prefix="/periodos",
    tags=["Periodos"]
)


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


@router.get(
    "/{periodo_id}/previsualizar-cierre"
)
def previsualizar_cierre(
    periodo_id: int,
    db: Session = Depends(get_db)
):
    try:
        return previsualizar_cierre_periodo(db, periodo_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@router.post(
    "/{periodo_id}/cerrar"
)
def cerrar_periodo(
    periodo_id: int,
    db: Session = Depends(get_db)
):
    try:
        periodo, resumen = cerrar_periodo_completo(db, periodo_id)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return {
        "periodo": {
            "id_periodo": periodo.id_periodo,
            "nombre": periodo.nombre,
            "fecha_inicio": periodo.fecha_inicio,
            "fecha_fin": periodo.fecha_fin,
            "estado": periodo.estado
        },
        "resumen": resumen
    }

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

    if cerrar_periodo:
        periodo_actualizado, _resumen = cerrar_periodo_completo(db, periodo_id)
        return periodo_actualizado

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

    if periodo.estado == "ACTIVO":
        marcar_otros_periodos_como_pendientes(db, periodo_id)
        db.commit()
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
