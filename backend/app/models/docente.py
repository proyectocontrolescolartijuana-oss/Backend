from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    Date,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class Docente(Base):
    __tablename__ = "docentes"

    id_docente = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_usuario = Column(
        BigInteger,
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    numero_empleado = Column(
        String(20),
        unique=True
    )

    especialidad = Column(
        String(150)
    )

    grado_academico = Column(
        String(100)
    )

    fecha_ingreso = Column(Date)

    estado = Column(
        Boolean,
        default=True
    )

    usuario = relationship("Usuario")

    grupos_materia = relationship(
        "GrupoMateria",
        back_populates="docente"
    )