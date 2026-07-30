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
    carta_unifront: bool = False
    carta_procedencia: bool = False


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
    carta_unifront: Optional[bool] = None
    carta_procedencia: Optional[bool] = None


class ServicioSocialEstatusUpdate(BaseModel):
    carta_unifront: bool
    carta_procedencia: bool


class ServicioSocialResponse(ServicioSocialBase):
    id_servicio: int

    class Config:
        from_attributes = True
