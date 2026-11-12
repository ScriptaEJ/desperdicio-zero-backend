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
from sqlalchemy.dialects.postgresql import UUID
from app.models.enums_model import (
    TipoRegistroPerda,
    MotivoPerda,
    Turno,
    UnidadeMedida
)
import uuid


class Perda(Base):
    __tablename__ = "perdas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    restaurante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurantes.id"),
        nullable=False
    )

    insumo_id = Column(
        UUID(as_uuid=True),
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