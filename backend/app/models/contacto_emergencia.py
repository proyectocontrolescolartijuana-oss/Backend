from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class ContactoEmergencia(Base):
    __tablename__ = "contactos_emergencia"

    id_contacto = Column(
        BigInteger,
        primary_key=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    nombre = Column(
        String(150),
        nullable=False
    )

    parentesco = Column(String(50))
    telefono = Column(String(20))
    correo = Column(String(150))

    direccion = Column(Text)

    contacto_principal = Column(
        Boolean,
        default=False
    )

    alumno = relationship(
        "Alumno",
        back_populates="contactos"
    )