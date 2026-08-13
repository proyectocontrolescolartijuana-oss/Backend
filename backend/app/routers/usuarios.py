from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate
)

from app.crud.crud_usuario import (
    get_usuarios,
    get_usuario,
    create_usuario,
    update_usuario,
    delete_usuario
)
from app.crud.crud_usuario_expediente import get_usuario_expediente

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

ROLES_PASSWORD_CONTROL_ESCOLAR = {"ALUMNO", "DOCENTE"}
ROLES_PASSWORD_RESTRINGIDOS = {"ADMIN", "CONTROL_ESCOLAR"}

def _tiene_rol(usuario: Usuario, rol: str) -> bool:
    return any(usuario_rol.nombre == rol for usuario_rol in usuario.roles)

def _puede_actualizar_password(
    usuario_actual: Usuario,
    usuario_objetivo: Usuario
) -> bool:
    if _tiene_rol(usuario_actual, "ADMIN"):
        return True

    if not _tiene_rol(usuario_actual, "CONTROL_ESCOLAR"):
        return False

    roles_objetivo = {
        rol.nombre
        for rol in usuario_objetivo.roles
    }

    return (
        bool(roles_objetivo & ROLES_PASSWORD_CONTROL_ESCOLAR)
        and not bool(roles_objetivo & ROLES_PASSWORD_RESTRINGIDOS)
    )

@router.get(
    "/",
    response_model=list[UsuarioResponse]
)
def listar_usuarios(
    db: Session = Depends(get_db)
):
    return get_usuarios(db)

@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    usuario = get_usuario(db, usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return usuario


@router.get(
    "/{usuario_id}/expediente"
)
def obtener_usuario_con_expediente(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    expediente = get_usuario_expediente(db, usuario_id)

    if not expediente:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return expediente

@router.post(
    "/",
    response_model=UsuarioResponse
)
def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    return create_usuario(db, usuario)

@router.patch(
    "/{usuario_id}",
    response_model=UsuarioResponse
)
def actualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user)
):
    usuario_objetivo = get_usuario(db, usuario_id)

    if not usuario_objetivo:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    if usuario.password is not None and not _puede_actualizar_password(
        usuario_actual,
        usuario_objetivo
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Control escolar solo puede cambiar la contraseña de "
                "alumnos y docentes"
            )
        )

    usuario_actualizado = update_usuario(
        db,
        usuario_id,
        usuario
    )

    if not usuario_actualizado:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    return usuario_actualizado

@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    eliminado = delete_usuario(db, usuario_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )
