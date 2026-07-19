from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text
)

from sqlalchemy.orm import relationship

from app.database import Base

class Empresa(Base):
    __tablename__ = "empresas"

    id_empresa = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    nombre = Column(String(150))

    direccion = Column(Text)

    telefono = Column(String(20))

    correo = Column(String(100))

    servicios = relationship(
        "ServicioSocial",
        back_populates="empresa"
    )

    practicas = relationship(
        "PracticaProfesional",
        back_populates="empresa"
    )