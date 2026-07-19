from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
    Text,
    TIMESTAMP,
    ForeignKey,
    Integer,
    func
)

from sqlalchemy.orm import relationship

from app.database import Base

class DocumentoAlumno(Base):
    __tablename__ = "documentos_alumno"

    id_documento = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno")
    )

    id_tipo_documento = Column(
        Integer,
        ForeignKey(
            "tipos_documento.id_tipo_documento"
        )
    )

    nombre_archivo = Column(
        String(255)
    )

    ruta_archivo = Column(
        String(500)
    )

    fecha_subida = Column(
        TIMESTAMP,
        server_default=func.current_timestamp()
    )

    validado = Column(
        Boolean,
        default=False
    )

    observaciones = Column(Text)

    alumno = relationship("Alumno")

    tipo_documento = relationship(
        "TipoDocumento",
        back_populates="documentos"
    )