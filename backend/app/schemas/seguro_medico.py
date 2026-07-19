from typing import Optional

from pydantic import BaseModel


class SeguroMedicoBase(BaseModel):
    id_alumno: int
    tiene_seguro: Optional[bool] = False
    institucion: Optional[str] = None
    numero_poliza: Optional[str] = None


class SeguroMedicoCreate(SeguroMedicoBase):
    pass


class SeguroMedicoUpdate(BaseModel):
    id_alumno: Optional[int] = None
    tiene_seguro: Optional[bool] = None
    institucion: Optional[str] = None
    numero_poliza: Optional[str] = None


class SeguroMedicoResponse(SeguroMedicoBase):
    id_seguro: int

    class Config:
        from_attributes = True
