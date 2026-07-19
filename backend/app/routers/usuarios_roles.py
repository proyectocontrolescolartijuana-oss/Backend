from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_usuario_rol import (
    create_usuario_rol,
    delete_usuario_rol,
    get_usuario_rol
)
from app.crud.crud_detalles import get_usuarios_roles_detalle
from app.database import get_db
from app.schemas.detalles import UsuarioRolDetalleResponse
from app.schemas.usuario_rol import UsuarioRolCreate, UsuarioRolResponse


router = APIRouter(
    prefix="/usuarios-roles",
    tags=["Usuarios roles"]
)


@router.get(
    "/",
    response_model=list[UsuarioRolDetalleResponse]
)
def listar_usuarios_roles(
    db: Session = Depends(get_db)
):
    return get_usuarios_roles_detalle(db)


@router.get(
    "/{usuario_id}/{rol_id}",
    response_model=UsuarioRolResponse
)
def obtener_usuario_rol(
    usuario_id: int,
    rol_id: int,
    db: Session = Depends(get_db)
):
    relacion = get_usuario_rol(db, usuario_id, rol_id)

    if not relacion:
        raise HTTPException(
            status_code=404,
            detail="Relacion usuario rol no encontrada"
        )

    return relacion


@router.post(
    "/",
    response_model=UsuarioRolResponse
)
def crear_usuario_rol(
    relacion: UsuarioRolCreate,
    db: Session = Depends(get_db)
):
    return create_usuario_rol(
        db,
        relacion.id_usuario,
        relacion.id_rol
    )


@router.delete(
    "/{usuario_id}/{rol_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_usuario_rol(
    usuario_id: int,
    rol_id: int,
    db: Session = Depends(get_db)
):
    eliminada = delete_usuario_rol(db, usuario_id, rol_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Relacion usuario rol no encontrada"
        )
