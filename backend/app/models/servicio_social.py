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

class ServicioSocial(Base):
    __tablename__ = "servicio_social"

    id_servicio = Column(
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

    horas_requeridas = Column(Integer)

    horas_completadas = Column(Integer)

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
        back_populates="servicios"
    )