from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentoEgresadoResponse(BaseModel):
    id_documento: int
    id_alumno: int
    tipo: str
    nombre_archivo: str
    ruta_archivo: str
    fecha_subida: Optional[datetime] = None

    class Config:
        from_attributes = True
