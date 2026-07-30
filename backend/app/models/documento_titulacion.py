from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class DocumentoTitulacion(Base):
    __tablename__ = "documentos_titulacion"

    id_documento_titulacion = Column(BigInteger, primary_key=True, index=True)
    id_titulacion = Column(
        BigInteger,
        ForeignKey("titulacion.id_titulacion"),
        nullable=False,
    )
    requisito = Column(String(100), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    observaciones = Column(Text)
    fecha_subida = Column(DateTime, server_default=func.now())

    titulacion = relationship("Titulacion", back_populates="documentos")
