from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DECIMAL,
    Date,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class HistorialAcademico(Base):
    __tablename__ = "historial_academico"

    id_historial = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    id_materia = Column(
        BigInteger,
        ForeignKey("materias.id_materia")
    )

    id_periodo = Column(
        Integer,
        ForeignKey("periodos.id_periodo")
    )

    tipo_evaluacion = Column(
        Enum(
            "ORDINARIO",
            "EXTRAORDINARIO"
        )
    )

    oportunidad = Column(Integer)

    calificacion_final = Column(
        DECIMAL(5,2)
    )

    resultado = Column(
        Enum(
            "APROBADO",
            "REPROBADO",
            "NP"
        )
    )

    fecha_cierre = Column(Date)

    alumno = relationship("Alumno")

    materia = relationship("Materia")

    periodo = relationship("Periodo")