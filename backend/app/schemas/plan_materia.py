from pydantic import BaseModel
from typing import Optional
from .materia import MateriaSimple
from .cuatrimestre import CuatrimestreSimple


class PlanMateriaBase(BaseModel):
    id_materia: int
    id_cuatrimestre: int
    obligatoria: bool = True


class PlanMateriaCreate(PlanMateriaBase):
    pass


class PlanMateriaUpdate(BaseModel):
    id_materia: Optional[int] = None
    id_cuatrimestre: Optional[int] = None
    obligatoria: Optional[bool] = None


class PlanMateriaUpsert(PlanMateriaBase):
    id_plan_materia: Optional[int] = None


class PlanMateriaResponse(PlanMateriaBase):
    id_plan_materia: int
    id_plan: int
    materia: MateriaSimple
    cuatrimestre: CuatrimestreSimple

    class Config:
        from_attributes = True
