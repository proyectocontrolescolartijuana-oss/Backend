from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Date,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class PracticaProfesional(Base):
    __tablename__ = "practicas_profesionales"

    id_practica = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    id_empresa = Column(
        BigInteger,
        ForeignKey("empresas.id_empresa")
    )

    proyecto = Column(String(255))

    asesor_empresa = Column(String(150))

    asesor_universidad = Column(String(150))

    fecha_inicio = Column(Date)

    fecha_fin = Column(Date)

    estado = Column(
        Enum(
            "EN_PROCESO",
            "COMPLETADO"
        )
    )

    alumno = relationship("Alumno")

    empresa = relationship(
        "Empresa",
        back_populates="practicas"
    )