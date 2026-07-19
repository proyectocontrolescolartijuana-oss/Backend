from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentoAlumnoBase(BaseModel):
    id_alumno: int
    id_tipo_documento: int
    nombre_archivo: Optional[str] = None
    ruta_archivo: Optional[str] = None
    validado: Optional[bool] = False
    observaciones: Optional[str] = None


class DocumentoAlumnoCreate(DocumentoAlumnoBase):
    pass


class DocumentoAlumnoUpdate(BaseModel):
    id_alumno: Optional[int] = None
    id_tipo_documento: Optional[int] = None
    nombre_archivo: Optional[str] = None
    ruta_archivo: Optional[str] = None
    validado: Optional[bool] = None
    observaciones: Optional[str] = None


class DocumentoAlumnoResponse(DocumentoAlumnoBase):
    id_documento: int
    fecha_subida: datetime

    class Config:
        from_attributes = True
