from datetime import datetime, timezone
from math import ceil
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.exceptions.exceptions import RestauranteNaoEncontrado, RestauranteJaExiste
from app.models.restaurante_model import Restaurante
from app.schemas.restaurante_schema import (
    RestauranteResponse,
    RestaurantesPaginados,
    UpdateRestaurante,
    createRestaurante,
)

#-------logic for restaurante services-------
def create_restaurante(db: Session, restaurante: createRestaurante) -> RestauranteResponse:
    novo_restaurante = Restaurante(
        nome=restaurante.nome,
        cwid=restaurante.cwid,
        custo_medio_kg=restaurante.custo_medio_kg,
        criado_em=datetime.now(timezone.utc)
    )
    if db.query(Restaurante).filter(Restaurante.nome == novo_restaurante.nome).first():
        raise RestauranteJaExiste
        
    db.add(novo_restaurante)
    db.commit()
    db.refresh(novo_restaurante)
    return RestauranteResponse.from_orm(novo_restaurante)

def get_restaurante_by_id(db: Session, restaurante_id: int) -> Optional[RestauranteResponse]:
    restaurante = db.query(Restaurante).filter(Restaurante.id == restaurante_id).first()
    if restaurante:
        return RestauranteResponse.from_orm(restaurante)
    return None

def get_restaurantes_paginated(db: Session, page: int, size: int) -> RestaurantesPaginados:
    total = db.query(func.count(Restaurante.id)).scalar()
    total_pages = ceil(total / size) if size > 0 else 0
    restaurantes = (
        db.query(Restaurante)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    items = [RestauranteResponse.from_orm(restaurante) for restaurante in restaurantes]
    return RestaurantesPaginados(
        page=page,
        size=size,
        total=total,
        total_pages=total_pages,
        items=items
    )

def update_restaurante(db: Session, restaurante_id: int, restaurante_update: UpdateRestaurante) -> Optional[RestauranteResponse]:
    restaurante = db.query(Restaurante).filter(Restaurante.id == restaurante_id).first()
    if not restaurante:
        return RestauranteNaoEncontrado

    if restaurante_update.nome is not None:
        restaurante.nome = restaurante_update.nome
    if restaurante_update.cwid is not None:
        restaurante.cwid = restaurante_update.cwid
    if restaurante_update.custo_medio_kg is not None:
        restaurante.custo_medio_kg = restaurante_update.custo_medio_kg

    db.commit()
    db.refresh(restaurante)
    return RestauranteResponse.from_orm(restaurante)

def delete_restaurante(db: Session, restaurante_id: int) -> bool:
    restaurante = db.query(Restaurante).filter(Restaurante.id == restaurante_id).first()
    if not restaurante:
        return RestauranteNaoEncontrado

    db.delete(restaurante)
    db.commit()
    return True

