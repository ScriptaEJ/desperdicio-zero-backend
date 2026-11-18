
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums_model import (
    TipoRegistroPerda,
    MotivoPerda,
    Turno,
    UnidadeMedida
)


class CreatePerda(BaseModel):
    restaurante_id: UUID
    insumo_id: UUID | None = None
    tipo_registro: TipoRegistroPerda
    quantidade: Decimal = Field(gt=0)
    unidade_medida: UnidadeMedida
    custo_unitario: Decimal = Field(ge=0)
    motivo: MotivoPerda
    turno: Turno | None = None
    observacao: str | None = None
    data_perda: datetime


class UpdatePerda(BaseModel):
    insumo_id: UUID | None = None
    tipo_registro: TipoRegistroPerda | None = None
    quantidade: Decimal | None = Field(default=None, gt=0)
    unidade_medida: UnidadeMedida | None = None
    custo_unitario: Decimal | None = Field(default=None, ge=0)
    motivo: MotivoPerda | None = None
    turno: Turno | None = None
    observacao: str | None = None
    data_perda: datetime | None = None


class PerdaResponse(BaseModel):
    id: UUID
    restaurante_id: UUID
    insumo_id: UUID | None
    usuario_id: int
    tipo_registro: TipoRegistroPerda
    quantidade: Decimal
    unidade_medida: UnidadeMedida
    custo_unitario: Decimal
    valor_total: Decimal
    motivo: MotivoPerda
    turno: Turno | None
    observacao: str | None
    data_perda: datetime
    criado_em: datetime | None

    model_config = ConfigDict(from_attributes=True)


class PerdasPaginadas(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    items: list[PerdaResponse]
