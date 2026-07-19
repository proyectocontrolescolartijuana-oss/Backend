from typing import Optional

from pydantic import BaseModel


class TipoDocumentoBase(BaseModel):
    nombre: Optional[str] = None


class TipoDocumentoCreate(TipoDocumentoBase):
    pass


class TipoDocumentoUpdate(BaseModel):
    nombre: Optional[str] = None


class TipoDocumentoResponse(TipoDocumentoBase):
    id_tipo_documento: int

    class Config:
        from_attributes = True
