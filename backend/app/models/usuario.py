from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    TIMESTAMP,
    func
)

from sqlalchemy.orm import relationship
from app.models.usuario_rol import usuario_roles
from app.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100))
    correo = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    telefono = Column(String(20))

    estado = Column(
        Enum("ACTIVO", "INACTIVO"),
        default="ACTIVO"
    )

    fecha_creacion = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    roles = relationship(
        "Rol",
        secondary=usuario_roles,
        back_populates="usuarios"
    )