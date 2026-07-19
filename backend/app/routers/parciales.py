from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.parcial import (
    ParcialCreate,
    ParcialResponse,
    ParcialUpdate
)

from app.crud.crud_parcial import (
    get_parciales,
    get_parcial,
    create_parcial,
    update_parcial,
    delete_parcial
)

router = APIRouter(
    prefix="/parciales",
    tags=["Parciales"]
)



@router.get(
    "/",
    response_model=list[ParcialResponse]
)
def listar_parciales(
    db: Session = Depends(get_db)
):
    return get_parciales(db)

@router.get(
    "/{parcial_id}",
    response_model=ParcialResponse
)
def obtener_parcial(
    parcial_id: int,
    db: Session = Depends(get_db)
):
    parcial = get_parcial(db, parcial_id)

    if not parcial:
        raise HTTPException(
            status_code=404,
            detail="Parcial no encontrado"
        )

    return parcial

@router.post(
    "/",
    response_model=ParcialResponse
)
def crear_parcial(
    parcial: ParcialCreate,
    db: Session = Depends(get_db)
):
    return create_parcial(
        db,
        parcial
    )

@router.patch(
    "/{parcial_id}",
    response_model=ParcialResponse
)
def actualizar_parcial(
    parcial_id: int,
    parcial: ParcialUpdate,
    db: Session = Depends(get_db)
):
    parcial_actualizado = update_parcial(
        db,
        parcial_id,
        parcial
    )

    if not parcial_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Parcial no encontrado"
        )

    return parcial_actualizado

@router.delete(
    "/{parcial_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_parcial(
    parcial_id: int,
    db: Session = Depends(get_db)
):
    eliminado = delete_parcial(db, parcial_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Parcial no encontrado"
        )
