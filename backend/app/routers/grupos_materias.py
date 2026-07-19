from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_detalles import (
    get_grupo_materia_detalle,
    get_grupos_materias_detalle
)
from app.crud.crud_grupo_materia import (
    create_grupo_materia,
    delete_grupo_materia,
    get_grupo_materia,
    update_grupo_materia
)
from app.database import get_db
from app.models.grupo_materia import GrupoMateria
from app.schemas.detalles import GrupoMateriaDetalleResponse
from app.schemas.grupo_materia import GrupoMateriaCreate, GrupoMateriaUpdate


router = APIRouter(
    prefix="/grupos-materias",
    tags=["Grupos materias"]
)


def _validar_grupo_materia_unica(
    db: Session,
    *,
    id_grupo: int,
    id_materia: int,
    id_periodo: int,
    excluir_id: Optional[int] = None
):
    query = db.query(GrupoMateria).filter(
        GrupoMateria.id_grupo == id_grupo,
        GrupoMateria.id_materia == id_materia,
        GrupoMateria.id_periodo == id_periodo
    )

    if excluir_id is not None:
        query = query.filter(GrupoMateria.id_grupo_materia != excluir_id)

    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La materia ya esta asignada a ese grupo y periodo"
        )


@router.get(
    "/",
    response_model=list[GrupoMateriaDetalleResponse]
)
def listar_grupos_materias(
    grupo_id: Optional[int] = None,
    docente_id: Optional[int] = None,
    materia_id: Optional[int] = None,
    periodo_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return get_grupos_materias_detalle(
        db,
        grupo_id=grupo_id,
        docente_id=docente_id,
        materia_id=materia_id,
        periodo_id=periodo_id
    )


@router.get(
    "/{grupo_materia_id}",
    response_model=GrupoMateriaDetalleResponse
)
def obtener_grupo_materia(
    grupo_materia_id: int,
    db: Session = Depends(get_db)
):
    grupo_materia = get_grupo_materia_detalle(db, grupo_materia_id)

    if not grupo_materia:
        raise HTTPException(
            status_code=404,
            detail="Grupo materia no encontrado"
        )

    return grupo_materia


@router.post(
    "/",
    response_model=GrupoMateriaDetalleResponse
)
def crear_grupo_materia(
    grupo_materia: GrupoMateriaCreate,
    db: Session = Depends(get_db)
):
    _validar_grupo_materia_unica(
        db,
        id_grupo=grupo_materia.id_grupo,
        id_materia=grupo_materia.id_materia,
        id_periodo=grupo_materia.id_periodo
    )

    nuevo_grupo_materia = create_grupo_materia(db, grupo_materia)

    return get_grupo_materia_detalle(db, nuevo_grupo_materia.id_grupo_materia)


@router.patch(
    "/{grupo_materia_id}",
    response_model=GrupoMateriaDetalleResponse
)
def actualizar_grupo_materia(
    grupo_materia_id: int,
    grupo_materia: GrupoMateriaUpdate,
    db: Session = Depends(get_db)
):
    grupo_materia_actual = get_grupo_materia(db, grupo_materia_id)

    if not grupo_materia_actual:
        raise HTTPException(
            status_code=404,
            detail="Grupo materia no encontrado"
        )

    update_data = grupo_materia.model_dump(exclude_unset=True)
    _validar_grupo_materia_unica(
        db,
        id_grupo=update_data.get("id_grupo", grupo_materia_actual.id_grupo),
        id_materia=update_data.get(
            "id_materia",
            grupo_materia_actual.id_materia
        ),
        id_periodo=update_data.get(
            "id_periodo",
            grupo_materia_actual.id_periodo
        ),
        excluir_id=grupo_materia_id
    )

    grupo_materia_actualizado = update_grupo_materia(
        db,
        grupo_materia_id,
        grupo_materia
    )

    if not grupo_materia_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Grupo materia no encontrado"
        )

    return get_grupo_materia_detalle(db, grupo_materia_id)


@router.delete(
    "/{grupo_materia_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_grupo_materia(
    grupo_materia_id: int,
    db: Session = Depends(get_db)
):
    eliminado = delete_grupo_materia(db, grupo_materia_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Grupo materia no encontrado"
        )
