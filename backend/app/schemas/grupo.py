from typing import Optional

from pydantic import BaseModel


class GrupoBase(BaseModel):
    nombre: Optional[str] = None
    id_carrera: int
    id_cuatrimestre: int
    id_plan: Optional[int] = None
    turno: Optional[str] = None


class GrupoCreate(GrupoBase):
    pass


class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    id_carrera: Optional[int] = None
    id_cuatrimestre: Optional[int] = None
    turno: Optional[str] = None


class GrupoResponse(GrupoBase):
    id_grupo: int

    class Config:
        from_attributes = True
