from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Date,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class CargaAcademica(Base):
    __tablename__ = "carga_academica"

    id_carga = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    id_grupo_materia = Column(
        BigInteger,
        ForeignKey(
            "grupos_materias.id_grupo_materia"
        )
    )

    oportunidad = Column(
        Enum(
            "ORDINARIO",
            "EXTRAORDINARIO"
        )
    )

    intento = Column(Integer)

    estatus = Column(
        Enum(
            "CURSANDO",
            "APROBADA",
            "REPROBADA",
            "NP",
            "BAJA"
        ),
        default="CURSANDO"
    )

    fecha_inscripcion = Column(Date)

    alumno = relationship("Alumno")

    grupo_materia = relationship(
        "GrupoMateria",
        back_populates="cargas"
    )