from pydantic import BaseModel, Field

class LoginSchema(BaseModel):
    correo: str
    password: str


class PasswordUpdate(BaseModel):
    password_actual: str = Field(min_length=1)
    nueva_password: str = Field(min_length=8)
