# app/models/insumo.py

from app.database.database import Base
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Numeric,
    DateTime,
    ForeignKey,
    Enum,
    Integer,
    text
)
from app.models.enums_model import CategoriaInsumos, UnidadeMedida


class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)

    restaurante_id = Column(
        Integer,
        ForeignKey("restaurantes.id"),
        nullable=False
    )

    nome = Column(String(150), nullable=False)

    categoria = Column(
        Enum(CategoriaInsumos, name="categoria_insumos"),
        nullable=False
    )

    unidade_medida = Column(
        Enum(UnidadeMedida, name="unidade_medida"),
        nullable=False
    )

    custo_unitario = Column(Numeric(12, 2), nullable=False)

    estoque_minimo = Column(Numeric(12, 3))

    ativo = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true")
    )

    criado_em = Column(DateTime(timezone=True))