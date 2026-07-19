from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.titulacion import (
    TitulacionCreate,
    TitulacionResponse,
    TitulacionUpdate
)

from app.crud.crud_titulacion import (
    get_titulaciones,
    get_titulacion,
    create_titulacion,
    update_titulacion,
    delete_titulacion
)

router = APIRouter(
    prefix="/titulaciones",
    tags=["Titulacion"]
)



@router.get(
    "/",
    response_model=list[TitulacionResponse]
)
def listar_titulaciones(
    db: Session = Depends(get_db)
):
    return get_titulaciones(db)

@router.get(
    "/{titulacion_id}",
    response_model=TitulacionResponse
)
def obtener_titulacion(
    titulacion_id: int,
    db: Session = Depends(get_db)
):
    titulacion = get_titulacion(db, titulacion_id)

    if not titulacion:
        raise HTTPException(
            status_code=404,
            detail="Titulacion no encontrada"
        )

    return titulacion

@router.post(
    "/",
    response_model=TitulacionResponse
)
def crear_titulacion(
    titulacion: TitulacionCreate,
    db: Session = Depends(get_db)
):
    return create_titulacion(
        db,
        titulacion
    )

@router.patch(
    "/{titulacion_id}",
    response_model=TitulacionResponse
)
def actualizar_titulacion(
    titulacion_id: int,
    titulacion: TitulacionUpdate,
    db: Session = Depends(get_db)
):
    titulacion_actualizada = update_titulacion(
        db,
        titulacion_id,
        titulacion
    )

    if not titulacion_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Titulacion no encontrada"
        )

    return titulacion_actualizada

@router.delete(
    "/{titulacion_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_titulacion(
    titulacion_id: int,
    db: Session = Depends(get_db)
):
    eliminada = delete_titulacion(db, titulacion_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Titulacion no encontrada"
        )
