from typing import Optional

from pydantic import BaseModel


class ContactoEmergenciaBase(BaseModel):
    id_alumno: int
    nombre: str
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    contacto_principal: Optional[bool] = False


class ContactoEmergenciaCreate(ContactoEmergenciaBase):
    pass


class ContactoEmergenciaUpdate(BaseModel):
    id_alumno: Optional[int] = None
    nombre: Optional[str] = None
    parentesco: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    contacto_principal: Optional[bool] = None


class ContactoEmergenciaResponse(ContactoEmergenciaBase):
    id_contacto: int

    class Config:
        from_attributes = True
