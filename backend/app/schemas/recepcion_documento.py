from datetime import date
from typing import Optional

from pydantic import BaseModel


class RecepcionDocumentoBase(BaseModel):
    id_alumno: int
    ficha_inscripcion: Optional[bool] = False
    acta_original: Optional[bool] = False
    acta_copias: Optional[bool] = False
    certificado_original: Optional[bool] = False
    constancia_terminacion: Optional[bool] = False
    fotografias: Optional[bool] = False
    curp_documento: Optional[bool] = False
    fecha_recepcion: Optional[date] = None
    recibido_por: Optional[int] = None
    observaciones: Optional[str] = None


class RecepcionDocumentoCreate(RecepcionDocumentoBase):
    pass


class RecepcionDocumentoUpdate(BaseModel):
    id_alumno: Optional[int] = None
    ficha_inscripcion: Optional[bool] = None
    acta_original: Optional[bool] = None
    acta_copias: Optional[bool] = None
    certificado_original: Optional[bool] = None
    constancia_terminacion: Optional[bool] = None
    fotografias: Optional[bool] = None
    curp_documento: Optional[bool] = None
    fecha_recepcion: Optional[date] = None
    recibido_por: Optional[int] = None
    observaciones: Optional[str] = None


class RecepcionDocumentoResponse(RecepcionDocumentoBase):
    id_recepcion: int

    class Config:
        from_attributes = True
