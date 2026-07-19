from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    Date,
    Text,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.database import Base

class Titulacion(Base):
    __tablename__ = "titulacion"

    id_titulacion = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    modalidad = Column(
        Enum(
            "PROMEDIO",
            "TESIS",
            "TESINA"
        )
    )

    cumple_promedio = Column(Boolean)

    servicio_social_liberado = Column(
        Boolean
    )

    practicas_liberadas = Column(
        Boolean
    )

    certificado_emitido = Column(
        Boolean
    )

    pagos_titulacion_completos = Column(
        Boolean
    )

    numero_autorizacion = Column(
        String(100)
    )

    acta_examen = Column(
        String(255)
    )

    titulo_emitido = Column(Boolean)

    fecha_titulacion = Column(Date)

    observaciones = Column(Text)

    alumno = relationship("Alumno")