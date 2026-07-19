from pydantic import BaseModel
from typing import Optional

class ParcialBase(BaseModel):
    nombre: str
    porcentaje: float

class ParcialCreate(ParcialBase):
    pass

class ParcialUpdate(BaseModel):
    nombre: Optional[str] = None
    porcentaje: Optional[float] = None

class ParcialResponse(ParcialBase):
    id_parcial: int

    class Config:
        from_attributes = True
