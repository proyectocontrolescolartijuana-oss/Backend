from datetime import date
from typing import Optional

from pydantic import BaseModel


class ProcedenciaAcademicaBase(BaseModel):
    id_alumno: int
    escuela_procedencia: Optional[str] = None
    nivel_academico: Optional[str] = None
    estado_procedencia: Optional[str] = None
    promedio_general: Optional[float] = None
    fecha_egreso: Optional[date] = None


class ProcedenciaAcademicaCreate(ProcedenciaAcademicaBase):
    pass


class ProcedenciaAcademicaUpdate(BaseModel):
    id_alumno: Optional[int] = None
    escuela_procedencia: Optional[str] = None
    nivel_academico: Optional[str] = None
    estado_procedencia: Optional[str] = None
    promedio_general: Optional[float] = None
    fecha_egreso: Optional[date] = None


class ProcedenciaAcademicaResponse(ProcedenciaAcademicaBase):
    id_procedencia: int

    class Config:
        from_attributes = True
