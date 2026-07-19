from datetime import date
from typing import Optional

from pydantic import BaseModel


class ServicioSocialBase(BaseModel):
    id_alumno: int
    id_empresa: int
    horas_requeridas: Optional[int] = None
    horas_completadas: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None


class ServicioSocialCreate(ServicioSocialBase):
    pass


class ServicioSocialUpdate(BaseModel):
    id_alumno: Optional[int] = None
    id_empresa: Optional[int] = None
    horas_requeridas: Optional[int] = None
    horas_completadas: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None


class ServicioSocialResponse(ServicioSocialBase):
    id_servicio: int

    class Config:
        from_attributes = True
