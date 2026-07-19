from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.materia import (
    MateriaCreate,
    MateriaResponse,
    MateriaUpdate
)
from app.crud.crud_materia import (
    get_materias,
    get_materia,
    create_materia,
    update_materia,
    delete_materia
)

router = APIRouter(
    prefix="/materias",
    tags=["Materias"]
)

@router.get(
    "/",
    response_model=list[MateriaResponse]
)
def listar_materias(
    db: Session = Depends(get_db)
):
    return get_materias(db)

@router.get(
    "/{materia_id}",
    response_model=MateriaResponse
)
def obtener_materia(
    materia_id: int,
    db: Session = Depends(get_db)
):
    materia = get_materia(db, materia_id)

    if not materia:
        raise HTTPException(
            status_code=404,
            detail="Materia no encontrada"
        )

    return materia

@router.post(
    "/",
    response_model=MateriaResponse
)
def crear_materia(
    materia: MateriaCreate,
    db: Session = Depends(get_db)
):
    return create_materia(db, materia)

@router.patch(
    "/{materia_id}",
    response_model=MateriaResponse
)
def actualizar_materia(
    materia_id: int,
    materia: MateriaUpdate,
    db: Session = Depends(get_db)
):
    materia_actualizada = update_materia(
        db,
        materia_id,
        materia
    )

    if not materia_actualizada:
        raise HTTPException(
            status_code=404,
            detail="Materia no encontrada"
        )

    return materia_actualizada

@router.delete(
    "/{materia_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_materia(
    materia_id: int,
    db: Session = Depends(get_db)
):
    eliminada = delete_materia(db, materia_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Materia no encontrada"
        )
