from datetime import date
from typing import Optional

from pydantic import BaseModel


class PracticaProfesionalBase(BaseModel):
    id_alumno: int
    id_empresa: int
    proyecto: Optional[str] = None
    asesor_empresa: Optional[str] = None
    asesor_universidad: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None


class PracticaProfesionalCreate(PracticaProfesionalBase):
    pass


class PracticaProfesionalUpdate(BaseModel):
    id_alumno: Optional[int] = None
    id_empresa: Optional[int] = None
    proyecto: Optional[str] = None
    asesor_empresa: Optional[str] = None
    asesor_universidad: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None


class PracticaProfesionalResponse(PracticaProfesionalBase):
    id_practica: int

    class Config:
        from_attributes = True
