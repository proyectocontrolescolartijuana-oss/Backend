from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)

from app.database import Base


class DocumentoEgresado(Base):
    __tablename__ = "documentos_egresado"
    __table_args__ = (
        UniqueConstraint("id_alumno", "tipo", name="uq_documento_egresado_tipo"),
    )

    id_documento = Column(BigInteger, primary_key=True, index=True)
    id_alumno = Column(
        BigInteger,
        ForeignKey("alumnos.id_alumno"),
        nullable=False,
    )
    tipo = Column(String(50), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    fecha_subida = Column(DateTime, server_default=func.now())
