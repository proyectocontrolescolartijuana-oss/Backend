from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    Boolean
)

from sqlalchemy.orm import relationship

from app.database import Base

class Carrera(Base):
    __tablename__ = "carreras"

    id_carrera = Column(
        Integer,
        primary_key=True,
        index=True
    )

    clave = Column(
        String(20),
        unique=True
    )

    rvoe = Column(
        String(30),
        unique=True
    )

    nombre = Column(
        String(150),
        nullable=False
    )

    nivel = Column(
        Enum(
            "TSU",
            "LICENCIATURA",
            "MAESTRIA",
            "INGENIERIA"
        ),
        nullable=False
    )

    duracion_cuatrimestres = Column(
        Integer,
        nullable=False
    )

    estado = Column(
        Boolean,
        default=True
    )
    
    logo = Column(
        String(255),
        nullable=True
    )

    planes = relationship(
        "PlanEstudio",
        back_populates="carrera"
    )
