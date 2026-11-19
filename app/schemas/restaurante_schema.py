# app/schemas/restaurante.py

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class createRestaurante(BaseModel):
    nome: str 
    cwid: Optional[str]
    custo_medio_kg: Decimal 

class RestauranteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    cwid: Optional[str]
    custo_medio_kg: Decimal
    criado_em: datetime

class RestaurantesPaginados(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    items: list[RestauranteResponse]    

class UpdateRestaurante(BaseModel):
    nome: Optional[str] = None
    cwid: Optional[str] = None
    custo_medio_kg: Optional[Decimal] = None

