
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums_model import CategoriaInsumos, UnidadeMedida


class CreateInsumo(BaseModel):
    restaurante_id: UUID
    nome: str = Field(min_length=1, max_length=150)
    categoria: CategoriaInsumos
    unidade_medida: UnidadeMedida
    custo_unitario: Decimal = Field(ge=0)
    estoque_minimo: Decimal | None = Field(default=None, ge=0)


class UpdateInsumo(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=150)
    categoria: CategoriaInsumos | None = None
    unidade_medida: UnidadeMedida | None = None
    custo_unitario: Decimal | None = Field(default=None, ge=0)
    estoque_minimo: Decimal | None = Field(default=None, ge=0)
    ativo: bool | None = None


class InsumoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    restaurante_id: UUID
    nome: str
    categoria: CategoriaInsumos
    unidade_medida: UnidadeMedida
    custo_unitario: Decimal
    estoque_minimo: Decimal | None
    ativo: bool
    criado_em: datetime | None
