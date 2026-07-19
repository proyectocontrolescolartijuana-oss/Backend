from sqlalchemy import (
    Column,
    Integer,
    String
)

from sqlalchemy.orm import relationship

from app.database import Base

class TipoDocumento(Base):
    __tablename__ = "tipos_documento"

    id_tipo_documento = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nombre = Column(
        String(100)
    )

    documentos = relationship(
        "DocumentoAlumno",
        back_populates="tipo_documento"
    )