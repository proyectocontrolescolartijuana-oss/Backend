from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    DECIMAL,
    Date,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class ProcedenciaAcademica(Base):
    __tablename__ = "procedencia_academica"

    id_procedencia = Column(
        BigInteger,
        primary_key=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno"),
        nullable=False
    )

    escuela_procedencia = Column(
        String(255)
    )

    nivel_academico = Column(
        Enum(
            "BACHILLERATO",
            "UNIVERSIDAD",
            "OTRO"
        )
    )

    estado_procedencia = Column(
        String(100)
    )

    promedio_general = Column(
        DECIMAL(5,2)
    )

    fecha_egreso = Column(Date)

    alumno = relationship(
        "Alumno",
        back_populates="procedencia"
    )