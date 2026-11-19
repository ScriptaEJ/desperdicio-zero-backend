
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class IndicadoresDashboard(BaseModel):
    custo_total: Decimal
    custo_anterior: Decimal
    variacao_percentual: Decimal | None


class OrigemDesperdicioItem(BaseModel):
    categoria: str
    valor_total: Decimal
    percentual: Decimal


class OrigemDesperdicioResponse(BaseModel):
    tipo: Literal["motivo", "turno"]
    custo_total: Decimal
    itens: list[OrigemDesperdicioItem]


class EvolucaoSemanalItem(BaseModel):
    inicio: date
    fim: date
    valor_total: Decimal


class EvolucaoSemanalResponse(BaseModel):
    total_semanas: int
    semanas: list[EvolucaoSemanalItem]

class PontoAtencaoItem(BaseModel):
    tipo: Literal["alerta", "atencao", "sucesso"]
    titulo: str
    descricao: str


class PontosAtencaoResponse(BaseModel):
    total_pontos: int
    pontos: list[PontoAtencaoItem]