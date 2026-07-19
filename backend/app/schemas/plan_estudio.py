from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from .carrera import CarreraSimple
from .materia import MateriaSimple

from app.schemas.plan_materia import (
    PlanMateriaCreate,
    PlanMateriaUpsert,
    PlanMateriaResponse
)

class MateriaAgrupada(BaseModel):
    id_plan_materia: int
    obligatoria: bool
    materia: MateriaSimple

    class Config:
        from_attributes = True


class CuatrimestreAgrupado(BaseModel):
    id_cuatrimestre: int
    nombre: str
    materias: List[MateriaAgrupada]


class PlanEstudioBase(BaseModel):
    id_carrera: int
    nombre_plan: str
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    vigente: bool = True


class PlanEstudioCreate(PlanEstudioBase):
    materias: List[PlanMateriaCreate] = Field(default_factory=list)


class PlanEstudioUpdate(BaseModel):
    id_carrera: Optional[int] = None
    nombre_plan: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    vigente: Optional[bool] = None
    materias: Optional[List[PlanMateriaUpsert]] = None


class PlanEstudioResponse(PlanEstudioBase):
    id_plan: int
    materias: List[PlanMateriaResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class PlanEstudioAgrupadoResponse(BaseModel):
    id_plan: int
    nombre_plan: str
    fecha_inicio: date | None
    fecha_fin: date | None
    vigente: bool

    carrera: CarreraSimple

    cuatrimestres: List[CuatrimestreAgrupado]

    class Config:
        from_attributes = True
