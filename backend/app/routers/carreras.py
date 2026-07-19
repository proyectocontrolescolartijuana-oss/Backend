from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.carrera import (
    CarreraCreate,
    CarreraResponse,
    CarreraUpdate
)

from app.crud.crud_carrera import (
    get_carreras,
    get_carrera,
    create_carrera,
    update_carrera,
    delete_carrera
)

router = APIRouter(
    prefix="/carreras",
    tags=["Carreras"]
)

@router.get(
    "/",
    response_model=list[CarreraResponse]
)
def listar_carreras(
    db: Session = Depends(get_db)
):
    return get_carreras(db)

@router.get(
    "/{carrera_id}",
    response_model=CarreraResponse
)
def obtener_carrera(
    carrera_id: int,
    db: Session = Depends(get_db)
):
    carrera = get_carrera(db, carrera_id)

    if not carrera:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    return carrera

@router.post(
    "/",
    response_model=CarreraResponse
)
def crear_carrera(
    carrera: CarreraCreate,
    db: Session = Depends(get_db)
):
    return create_carrera(db, carrera)

@router.patch(
    "/{carrera_id}",
    response_model=CarreraResponse
)
def actualizar_carrera(
    carrera_id: int,
    carrera: CarreraUpdate,
    db: Session = Depends(get_db)
):
    carrera_actualizada = update_carrera(
        db,
        carrera_id,
        carrera
    )

    if not carrera_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    return carrera_actualizada

@router.delete(
    "/{carrera_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_carrera(
    carrera_id: int,
    db: Session = Depends(get_db)
):
    eliminada = delete_carrera(db, carrera_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )
