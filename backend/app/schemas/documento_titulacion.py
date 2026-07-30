from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentoTitulacionBase(BaseModel):
    id_titulacion: int
    requisito: str
    nombre_archivo: str
    ruta_archivo: str
    observaciones: Optional[str] = None


class DocumentoTitulacionCreate(DocumentoTitulacionBase):
    pass


class DocumentoTitulacionResponse(DocumentoTitulacionBase):
    id_documento_titulacion: int
    fecha_subida: Optional[datetime] = None

    class Config:
        from_attributes = True
