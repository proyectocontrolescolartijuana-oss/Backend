from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    DECIMAL,
    Date,
    Text,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class Extraordinario(Base):
    __tablename__ = "extraordinarios"

    id_extraordinario = Column(
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

    intento = Column(Integer)

    fecha_examen = Column(Date)

    calificacion = Column(
        DECIMAL(5,2)
    )

    estatus = Column(
        Enum(
            "APROBADO",
            "REPROBADO",
            "NP"
        )
    )

    observaciones = Column(Text)

    alumno = relationship("Alumno")

    materia = relationship("Materia")