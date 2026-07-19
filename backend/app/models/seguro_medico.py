from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class SeguroMedico(Base):
    __tablename__ = "seguros_medicos"

    id_seguro = Column(
        BigInteger,
        primary_key=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    tiene_seguro = Column(
        Boolean,
        default=False
    )

    institucion = Column(
        String(150)
    )

    numero_poliza = Column(
        String(100)
    )

    alumno = relationship(
        "Alumno",
        back_populates="seguros"
    )