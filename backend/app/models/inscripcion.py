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

class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id_inscripcion = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    id_grupo = Column(
        BigInteger,
        ForeignKey("grupos.id_grupo")
    )

    id_periodo = Column(
        Integer,
        ForeignKey("periodos.id_periodo")
    )

    fecha_inscripcion = Column(Date)

    estado = Column(
        Enum(
            "ACTIVO",
            "BAJA",
            "FINALIZADO"
        ),
        default="ACTIVO"
    )

    alumno = relationship("Alumno")

    grupo = relationship("Grupo")

    periodo = relationship("Periodo")