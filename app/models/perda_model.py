# app/models/perda.py

from app.database.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
    Enum
)
from app.models.enums_model import (
    TipoRegistroPerda,
    MotivoPerda,
    Turno,
    UnidadeMedida
)


class Perda(Base):
    __tablename__ = "perdas"

    id = Column(Integer, primary_key=True, index=True)

    restaurante_id = Column(
        Integer,
        ForeignKey("restaurantes.id"),
        nullable=False
    )

    insumo_id = Column(
        Integer,
        ForeignKey("insumos.id"),
        nullable=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    tipo_registro = Column(
        Enum(TipoRegistroPerda, name="tipo_registro_perda"),
        nullable=False
    )

    quantidade = Column(Numeric(12, 3), nullable=False)

    unidade_medida = Column(
        Enum(UnidadeMedida, name="unidade_medida"),
        nullable=False
    )

    custo_unitario = Column(Numeric(12, 2), nullable=False)

    valor_total = Column(Numeric(12, 2), nullable=False)

    motivo = Column(
        Enum(MotivoPerda, name="motivo_perda"),
        nullable=False
    )

    turno = Column(
        Enum(Turno, name="turno")
    )

    observacao = Column(Text)

    data_perda = Column(DateTime(timezone=True), nullable=False)

    criado_em = Column(DateTime(timezone=True))