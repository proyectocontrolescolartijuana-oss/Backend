from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from app.crud.crud_plan_estudio import transformar_plan
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db

from app.schemas.plan_estudio import (
    PlanEstudioCreate,
    PlanEstudioResponse,
    PlanEstudioUpdate
)
from app.schemas.plan_materia import (
    PlanMateriaCreate,
    PlanMateriaResponse,
    PlanMateriaUpdate
)

from app.crud.crud_plan_estudio import (
    agregar_materia_a_plan,
    actualizar_materia_de_plan,
    crear_plan_estudio,
    actualizar_plan,
    eliminar_materia_de_plan,
    eliminar_plan,
    obtener_planes,
    obtener_plan_por_id
)

router = APIRouter(
    prefix="/planes-estudio",
    tags=["Planes de Estudio"]
)


def _bad_request(error: ValueError):
    raise HTTPException(
        status_code=400,
        detail=str(error)
    )


@router.post(
    "/",
    response_model=PlanEstudioResponse
)
def crear(
    plan: PlanEstudioCreate,
    db: Session = Depends(get_db)
):
    try:
        return crear_plan_estudio(db, plan)
    except ValueError as error:
        _bad_request(error)


@router.get("/")
def listar(
    db: Session = Depends(get_db)
):
    planes = obtener_planes(db)

    return [
        transformar_plan(plan)
        for plan in planes
    ]


@router.get("/{id_plan}")
def obtener(
    id_plan: int,
    db: Session = Depends(get_db)
):
    plan = obtener_plan_por_id(db, id_plan)

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan no encontrado"
        )

    return transformar_plan(plan)


@router.patch(
    "/{id_plan}",
    response_model=PlanEstudioResponse
)
@router.put(
    "/{id_plan}",
    response_model=PlanEstudioResponse
)
def actualizar(
    id_plan: int,
    datos: PlanEstudioUpdate,
    db: Session = Depends(get_db)
):
    try:
        plan = actualizar_plan(
            db,
            id_plan,
            datos
        )
    except ValueError as error:
        _bad_request(error)

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan de estudio no encontrado"
        )

    return plan


@router.post(
    "/{id_plan}/materias",
    response_model=PlanMateriaResponse
)
def agregar_materia(
    id_plan: int,
    materia: PlanMateriaCreate,
    db: Session = Depends(get_db)
):
    try:
        materia_plan = agregar_materia_a_plan(
            db,
            id_plan,
            materia
        )
    except ValueError as error:
        _bad_request(error)

    if not materia_plan:
        raise HTTPException(
            status_code=404,
            detail="Plan de estudio no encontrado"
        )

    return materia_plan


@router.patch(
    "/{id_plan}/materias/{id_plan_materia}",
    response_model=PlanMateriaResponse
)
def actualizar_materia(
    id_plan: int,
    id_plan_materia: int,
    materia: PlanMateriaUpdate,
    db: Session = Depends(get_db)
):
    try:
        materia_plan = actualizar_materia_de_plan(
            db,
            id_plan,
            id_plan_materia,
            materia
        )
    except ValueError as error:
        _bad_request(error)

    if not materia_plan:
        raise HTTPException(
            status_code=404,
            detail="Materia del plan no encontrada"
        )

    return materia_plan


@router.delete(
    "/{id_plan}/materias/{id_plan_materia}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_materia(
    id_plan: int,
    id_plan_materia: int,
    db: Session = Depends(get_db)
):
    eliminada = eliminar_materia_de_plan(
        db,
        id_plan,
        id_plan_materia
    )

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Materia del plan no encontrada"
        )


@router.delete(
    "/{id_plan}"
)
def eliminar(
    id_plan: int,
    db: Session = Depends(get_db)
):
    plan = eliminar_plan(db, id_plan)

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan de estudio no encontrado"
        )

    return {
        "message": "Plan eliminado correctamente"
    }
