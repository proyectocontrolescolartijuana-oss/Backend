from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    func,
)

from app.database import Base


class CierrePeriodo(Base):
    __tablename__ = "cierres_periodo"

    id_cierre = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    id_periodo_cerrado = Column(
        Integer,
        ForeignKey("periodos.id_periodo"),
        nullable=False,
    )

    id_periodo_activado = Column(
        Integer,
        ForeignKey("periodos.id_periodo"),
    )

    resumen_json = Column(Text)

    fecha_cierre = Column(
        DateTime,
        server_default=func.current_timestamp(),
    )
