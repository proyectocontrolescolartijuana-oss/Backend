from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Enum
)

from sqlalchemy.orm import relationship

from app.database import Base

class Periodo(Base):
    __tablename__ = "periodos"

    id_periodo = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre = Column(String(50))

    fecha_inicio = Column(Date)

    fecha_fin = Column(Date)

    estado = Column(
        Enum("ACTIVO", "CERRADO"),
        default="ACTIVO"
    )

    grupos_materia = relationship(
        "GrupoMateria",
        back_populates="periodo"
    )