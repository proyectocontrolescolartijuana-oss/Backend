from sqlalchemy import (
    Column,
    BigInteger,
    String
)

from sqlalchemy.orm import relationship

from app.database import Base

class Tutor(Base):
    __tablename__ = "tutores"

    id_tutor = Column(
        BigInteger,
        primary_key=True
    )

    nombre = Column(
        String(150),
        nullable=False
    )

    parentesco = Column(String(50))
    telefono = Column(String(20))
    correo = Column(String(100))
    ocupacion = Column(String(100))

    alumnos = relationship(
        "Alumno",
        secondary="alumno_tutor"
    )