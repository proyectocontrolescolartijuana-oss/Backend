from pydantic import BaseModel
from typing import Optional
from datetime import date

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

    class Config:
        from_attributes = True
