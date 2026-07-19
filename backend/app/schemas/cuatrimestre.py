from pydantic import BaseModel
from typing import Optional


class CuatrimestreBase(BaseModel):
    numero: int
    nombre: str


class CuatrimestreCreate(CuatrimestreBase):
    pass


class CuatrimestreUpdate(BaseModel):
    numero: Optional[int] = None
    nombre: Optional[str] = None


class CuatrimestreResponse(CuatrimestreBase):
    id_cuatrimestre: int

    class Config:
        from_attributes = True


class CuatrimestreSimple(BaseModel):
    id_cuatrimestre: int
    nombre: str

    class Config:
        from_attributes = True
