from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Date,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_carga = Column(
        BigInteger,
        ForeignKey("carga_academica.id_carga")
    )

    id_parcial = Column(
        Integer,
        ForeignKey("parciales.id_parcial")
    )

    fecha = Column(Date)

    asistencia = Column(Boolean)

    carga = relationship("CargaAcademica")

    parcial = relationship("Parcial")
