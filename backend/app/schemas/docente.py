from pydantic import BaseModel
from typing import Optional
from datetime import date


class DocenteUsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None

    class Config:
        from_attributes = True


class DocenteBase(BaseModel):
    id_usuario: int

    numero_empleado: Optional[str] = None

    especialidad: Optional[str] = None

    grado_academico: Optional[str] = None

    fecha_ingreso: Optional[date] = None

class DocenteCreate(DocenteBase):
    pass

class DocenteUpdate(BaseModel):
    id_usuario: Optional[int] = None
    numero_empleado: Optional[str] = None
    especialidad: Optional[str] = None
    grado_academico: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    estado: Optional[bool] = None

class DocenteResponse(DocenteBase):
    id_docente: int
    estado: bool
    usuario: Optional[DocenteUsuarioResponse] = None

    class Config:
        from_attributes = True
