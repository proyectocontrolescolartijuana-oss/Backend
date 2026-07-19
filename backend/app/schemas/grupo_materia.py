from typing import Optional

from pydantic import BaseModel


class GrupoMateriaBase(BaseModel):
    id_grupo: int
    id_materia: int
    id_docente: int
    id_periodo: int
    aula: Optional[str] = None
    cupo_maximo: Optional[int] = None


class GrupoMateriaCreate(GrupoMateriaBase):
    pass


class GrupoMateriaUpdate(BaseModel):
    id_grupo: Optional[int] = None
    id_materia: Optional[int] = None
    id_docente: Optional[int] = None
    id_periodo: Optional[int] = None
    aula: Optional[str] = None
    cupo_maximo: Optional[int] = None


class GrupoMateriaResponse(GrupoMateriaBase):
    id_grupo_materia: int

    class Config:
        from_attributes = True
