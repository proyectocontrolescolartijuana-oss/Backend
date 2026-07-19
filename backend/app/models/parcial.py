from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL
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

    porcentaje = Column(
        DECIMAL(5,2)
    )

    calificaciones = relationship(
        "Calificacion",
        back_populates="parcial"
    )