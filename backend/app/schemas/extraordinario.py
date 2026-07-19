from datetime import date
from typing import Optional

from pydantic import BaseModel


class ExtraordinarioBase(BaseModel):
    id_alumno: int
    id_materia: int
    intento: Optional[int] = None
    fecha_examen: Optional[date] = None
    calificacion: Optional[float] = None
    estatus: Optional[str] = None
    observaciones: Optional[str] = None


class ExtraordinarioCreate(ExtraordinarioBase):
    pass


class ExtraordinarioUpdate(BaseModel):
    id_alumno: Optional[int] = None
    id_materia: Optional[int] = None
    intento: Optional[int] = None
    fecha_examen: Optional[date] = None
    calificacion: Optional[float] = None
    estatus: Optional[str] = None
    observaciones: Optional[str] = None


class ExtraordinarioResponse(ExtraordinarioBase):
    id_extraordinario: int

    class Config:
        from_attributes = True
