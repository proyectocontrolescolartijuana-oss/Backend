from pydantic import BaseModel


class UsuarioRolBase(BaseModel):
    id_usuario: int
    id_rol: int


class UsuarioRolCreate(UsuarioRolBase):
    pass


class UsuarioRolResponse(UsuarioRolBase):
    pass
