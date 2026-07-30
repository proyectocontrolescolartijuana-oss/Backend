from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.materia import (
    MateriaCreate,
    MateriaResponse,
    MateriaUpdate
)
from app.schemas.materia_prerrequisito import (
    MateriaPrerrequisitoCreate,
    MateriaPrerrequisitoResponse,
    MateriaPrerrequisitoUpdate,
)
from app.crud.crud_materia import (
    get_materias,
    get_materia,
    create_materia,
    update_materia,
    delete_materia
)
from app.crud.crud_materia_prerrequisito import (
    actualizar_prerrequisito,
    crear_prerrequisito,
    eliminar_prerrequisito,
    listar_prerrequisitos,
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

@router.get(
    "/{materia_id}/prerrequisitos",
    response_model=list[MateriaPrerrequisitoResponse]
)
def obtener_prerrequisitos(
    materia_id: int,
    db: Session = Depends(get_db)
):
    materia = get_materia(db, materia_id)

    if not materia:
        raise HTTPException(
            status_code=404,
            detail="Materia no encontrada"
        )

    return listar_prerrequisitos(db, materia_id)

@router.post(
    "/{materia_id}/prerrequisitos",
    response_model=MateriaPrerrequisitoResponse
)
def agregar_prerrequisito(
    materia_id: int,
    prerrequisito: MateriaPrerrequisitoCreate,
    db: Session = Depends(get_db)
):
    try:
        nuevo_prerrequisito = crear_prerrequisito(
            db,
            materia_id,
            prerrequisito
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    if not nuevo_prerrequisito:
        raise HTTPException(
            status_code=404,
            detail="Materia no encontrada"
        )

    return nuevo_prerrequisito

@router.patch(
    "/{materia_id}/prerrequisitos/{prerrequisito_id}",
    response_model=MateriaPrerrequisitoResponse
)
def editar_prerrequisito(
    materia_id: int,
    prerrequisito_id: int,
    prerrequisito: MateriaPrerrequisitoUpdate,
    db: Session = Depends(get_db)
):
    try:
        prerrequisito_actualizado = actualizar_prerrequisito(
            db,
            materia_id,
            prerrequisito_id,
            prerrequisito
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    if not prerrequisito_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Prerrequisito no encontrado"
        )

    return prerrequisito_actualizado

@router.delete(
    "/{materia_id}/prerrequisitos/{prerrequisito_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def borrar_prerrequisito(
    materia_id: int,
    prerrequisito_id: int,
    db: Session = Depends(get_db)
):
    eliminado = eliminar_prerrequisito(
        db,
        materia_id,
        prerrequisito_id
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Prerrequisito no encontrado"
        )

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
