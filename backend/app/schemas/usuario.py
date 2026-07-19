from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.schemas.rol import RolResponse

class UsuarioBase(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    correo: EmailStr
    telefono: Optional[str] = None
    roles: List[str]

class UsuarioCreate(UsuarioBase):
    password: Optional[str] = None

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = None
    password: Optional[str] = None
    estado: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    roles: List[RolResponse]

    class Config:
        from_attributes = True
