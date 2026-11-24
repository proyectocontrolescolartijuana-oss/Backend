from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.usuario import Usuario

ROLES_ADMINISTRACION = ("ADMIN", "CONTROL_ESCOLAR")


def require_roles(
    *roles_permitidos: str,
    detalle: str = "No tienes permisos para realizar esta accion"
):
    """Dependencia de FastAPI: exige que el usuario tenga alguno de los roles."""
    permitidos = set(roles_permitidos)

    def dependencia(usuario: Usuario = Depends(get_current_user)):
        roles = {rol.nombre for rol in usuario.roles}

        if roles.isdisjoint(permitidos):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=detalle
            )

        return usuario

    return dependencia