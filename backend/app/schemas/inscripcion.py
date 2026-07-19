from datetime import date
from typing import Optional

from pydantic import BaseModel


class InscripcionBase(BaseModel):
    id_alumno: int
    id_grupo: int
    id_periodo: int
    fecha_inscripcion: Optional[date] = None
    estado: Optional[str] = "ACTIVO"


class InscripcionCreate(InscripcionBase):
    pass


class InscripcionUpdate(BaseModel):
    id_alumno: Optional[int] = None
    id_grupo: Optional[int] = None
    id_periodo: Optional[int] = None
    fecha_inscripcion: Optional[date] = None
    estado: Optional[str] = None


class InscripcionResponse(InscripcionBase):
    id_inscripcion: int

    class Config:
        from_attributes = True
