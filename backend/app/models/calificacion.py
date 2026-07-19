from sqlalchemy import (
    Column,
    BigInteger,
    DECIMAL,
    TIMESTAMP,
    ForeignKey,
    Integer,
    func
)

from sqlalchemy.orm import relationship

from app.database import Base

class Calificacion(Base):
    __tablename__ = "calificaciones"

    id_calificacion = Column(
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

    calificacion = Column(
        DECIMAL(5,2)
    )

    fecha_captura = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    capturado_por = Column(
        BigInteger,
        ForeignKey("usuarios.id_usuario")
    )

    carga = relationship("CargaAcademica")

    parcial = relationship(
        "Parcial",
        back_populates="calificaciones"
    )

    usuario = relationship("Usuario")