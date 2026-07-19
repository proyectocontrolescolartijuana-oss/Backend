from datetime import date
from typing import Optional

from pydantic import BaseModel


class CargaAcademicaBase(BaseModel):
    id_alumno: int
    id_grupo_materia: int
    oportunidad: str
    intento: Optional[int] = None
    estatus: Optional[str] = "CURSANDO"
    fecha_inscripcion: Optional[date] = None


class CargaAcademicaCreate(CargaAcademicaBase):
    pass


class CargaAcademicaUpdate(BaseModel):
    id_alumno: Optional[int] = None
    id_grupo_materia: Optional[int] = None
    oportunidad: Optional[str] = None
    intento: Optional[int] = None
    estatus: Optional[str] = None
    fecha_inscripcion: Optional[date] = None


class CargaAcademicaResponse(CargaAcademicaBase):
    id_carga: int

    class Config:
        from_attributes = True
