from pydantic import BaseModel
from datetime import date
from typing import Optional

class PeriodoBase(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date

class PeriodoCreate(PeriodoBase):
    pass

class PeriodoUpdate(BaseModel):
    nombre: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    estado: Optional[str] = None

class PeriodoResponse(PeriodoBase):
    id_periodo: int
    estado: str

    class Config:
        from_attributes = True
