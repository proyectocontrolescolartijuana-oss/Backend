from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    Date,
    Text,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class RecepcionDocumento(Base):
    __tablename__ = "recepcion_documentos"

    id_recepcion = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    ficha_inscripcion = Column(
        Boolean,
        default=False
    )

    acta_original = Column(
        Boolean,
        default=False
    )

    acta_copias = Column(
        Boolean,
        default=False
    )

    certificado_original = Column(
        Boolean,
        default=False
    )

    constancia_terminacion = Column(
        Boolean,
        default=False
    )

    fotografias = Column(
        Boolean,
        default=False
    )

    curp_documento = Column(
        Boolean,
        default=False
    )

    fecha_recepcion = Column(Date)

    recibido_por = Column(
        BigInteger,
        ForeignKey("usuarios.id_usuario")
    )

    observaciones = Column(Text)

    alumno = relationship("Alumno")

    usuario = relationship("Usuario")