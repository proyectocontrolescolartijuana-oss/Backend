from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class Grupo(Base):
    __tablename__ = "grupos"

    id_grupo = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    nombre = Column(String(50))

    id_carrera = Column(
        Integer,
        ForeignKey("carreras.id_carrera")
    )

    id_cuatrimestre = Column(
        Integer,
        ForeignKey("cuatrimestres.id_cuatrimestre")
    )

    turno = Column(
        Enum("MATUTINO", "VESPERTINO")
    )

    carrera = relationship("Carrera")

    cuatrimestre = relationship("Cuatrimestre")

    materias = relationship(
        "GrupoMateria",
        back_populates="grupo"
    )