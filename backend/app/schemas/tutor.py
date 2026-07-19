from typing import Optional

from pydantic import BaseModel


class TutorBase(BaseModel):
    nombre: str
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    ocupacion: Optional[str] = None


class TutorCreate(TutorBase):
    pass


class TutorUpdate(BaseModel):
    nombre: Optional[str] = None
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    ocupacion: Optional[str] = None


class TutorResponse(TutorBase):
    id_tutor: int

    class Config:
        from_attributes = True
