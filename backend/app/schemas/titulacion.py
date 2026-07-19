from pydantic import BaseModel
from typing import Optional
from datetime import date

class TitulacionBase(BaseModel):
    id_alumno: int

    modalidad: str

    cumple_promedio: bool

    servicio_social_liberado: bool

    practicas_liberadas: bool

    certificado_emitido: bool

    pagos_titulacion_completos: bool

    numero_autorizacion: Optional[str]

    acta_examen: Optional[str]

    titulo_emitido: bool

    fecha_titulacion: Optional[date]

    observaciones: Optional[str]

class TitulacionCreate(TitulacionBase):
    pass

class TitulacionUpdate(BaseModel):
    id_alumno: Optional[int] = None
    modalidad: Optional[str] = None
    cumple_promedio: Optional[bool] = None
    servicio_social_liberado: Optional[bool] = None
    practicas_liberadas: Optional[bool] = None
    certificado_emitido: Optional[bool] = None
    pagos_titulacion_completos: Optional[bool] = None
    numero_autorizacion: Optional[str] = None
    acta_examen: Optional[str] = None
    titulo_emitido: Optional[bool] = None
    fecha_titulacion: Optional[date] = None
    observaciones: Optional[str] = None

class TitulacionResponse(TitulacionBase):
    id_titulacion: int

    class Config:
        from_attributes = True
