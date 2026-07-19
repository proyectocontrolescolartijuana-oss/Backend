from datetime import date
from typing import Optional

from pydantic import BaseModel


class HistorialAcademicoBase(BaseModel):
    id_alumno: int
    id_materia: int
    id_periodo: int
    tipo_evaluacion: Optional[str] = None
    oportunidad: Optional[int] = None
    calificacion_final: Optional[float] = None
    resultado: Optional[str] = None
    fecha_cierre: Optional[date] = None


class HistorialAcademicoCreate(HistorialAcademicoBase):
    pass


class HistorialAcademicoUpdate(BaseModel):
    id_alumno: Optional[int] = None
    id_materia: Optional[int] = None
    id_periodo: Optional[int] = None
    tipo_evaluacion: Optional[str] = None
    oportunidad: Optional[int] = None
    calificacion_final: Optional[float] = None
    resultado: Optional[str] = None
    fecha_cierre: Optional[date] = None


class HistorialAcademicoResponse(HistorialAcademicoBase):
    id_historial: int

    class Config:
        from_attributes = True
