
from uuid import UUID
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.dashboard_schemas import (
    IndicadoresDashboard,
    OrigemDesperdicioResponse,
    EvolucaoSemanalResponse,
    PontosAtencaoResponse
)

from app.services.dashboard_services import (
    obter_indicadores,
    obter_origem_desperdicio,
    obter_evolucao, 
    obter_pontos_atencao
)


dashboard_routes = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@dashboard_routes.get(
    "/indicadores",
    response_model=IndicadoresDashboard
)
def listar_indicadores(
    restaurante_id: UUID,
    filtro: Literal[
        "esta_semana",
        "este_mes",
        "ultimos_90_dias"
    ] = Query("esta_semana"),
    db: Session = Depends(get_db)
):
    return obter_indicadores(
        db,
        restaurante_id,
        filtro
    )


@dashboard_routes.get(
    "/origem-desperdicio",
    response_model=OrigemDesperdicioResponse
)
def listar_origem_desperdicio(
    restaurante_id: UUID,
    filtro: Literal[
        "esta_semana",
        "este_mes",
        "ultimos_90_dias"
    ] = Query("esta_semana"),
    agrupamento: Literal[
        "motivo",
        "turno"
    ] = Query("motivo"),
    db: Session = Depends(get_db)
):
    return obter_origem_desperdicio(
        db,
        restaurante_id,
        filtro,
        agrupamento
    )


@dashboard_routes.get(
    "/evolucao",
    response_model=EvolucaoSemanalResponse
)
def listar_evolucao(
    restaurante_id: UUID,
    db: Session = Depends(get_db)
):
    return obter_evolucao(
        db,
        restaurante_id
    )

@dashboard_routes.get(
    "/pontos-atencao",
    response_model=PontosAtencaoResponse
)
def listar_pontos_atencao(
    restaurante_id: UUID,
    filtro: Literal[
        "esta_semana",
        "este_mes",
        "ultimos_90_dias"
    ] = Query("esta_semana"),
    db: Session = Depends(get_db)
):
    return obter_pontos_atencao(
        db,
        restaurante_id,
        filtro
    )