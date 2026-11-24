from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    Enum
)

from sqlalchemy.orm import relationship

from app.database import Base

class Parcial(Base):
    __tablename__ = "parciales"

    id_parcial = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre = Column(String(50))

    # Cada modalidad de carrera tiene su propio conjunto de parciales.
    modalidad = Column(
        Enum(
            "CUATRIMESTRAL",
            "SABATINA"
        ),
        nullable=False,
        default="CUATRIMESTRAL",
        server_default="CUATRIMESTRAL"
    )

    porcentaje = Column(
        DECIMAL(5,2)
    )

    calificaciones = relationship(
        "Calificacion",
        back_populates="parcial"
    )