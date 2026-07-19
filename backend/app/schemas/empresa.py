from typing import Optional

from pydantic import BaseModel


class EmpresaBase(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None


class EmpresaResponse(EmpresaBase):
    id_empresa: int

    class Config:
        from_attributes = True
