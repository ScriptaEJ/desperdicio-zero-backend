from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.middlewares.auth import autorizar_perfis
from app.schemas.insumos_schemas import CreateInsumo, UpdateInsumo, InsumoResponse
from app.services.insumos_services import (
    criar_insumo,
    listar_insumos,
    buscar_insumo,
    atualizar_insumo,
    deletar_insumo
)

insumos_routes = APIRouter(tags=["04. Insumos"])

@insumos_routes.post("/insumos", response_model=InsumoResponse, status_code=201, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def create_insumo(
    data: CreateInsumo,
    db: Session = Depends(get_db),
):
    return criar_insumo(data, db)

@insumos_routes.get("/insumos", response_model=list[InsumoResponse], dependencies=[Depends(autorizar_perfis("admin", "user"))])
def get_insumos(
    restaurante_id: str = Query(..., description="ID do restaurante"),
    db: Session = Depends(get_db),
):
    return listar_insumos(restaurante_id, db)

@insumos_routes.get("/insumos/{id}", response_model=InsumoResponse, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def get_insumo_by_id(
    id: str,
    db: Session = Depends(get_db),
):
    insumo = buscar_insumo(id, db)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return insumo

@insumos_routes.patch("/insumos/{id}", response_model=InsumoResponse, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def update_insumo_by_id(
    id: str,
    data: UpdateInsumo,
    db: Session = Depends(get_db),
):
    insumo = atualizar_insumo(id, data, db)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return insumo

@insumos_routes.delete("/insumos/{id}", response_model=InsumoResponse, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def delete_insumo_by_id(
    id: str,
    db: Session = Depends(get_db),
):
    insumo = deletar_insumo(id, db)
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não encontrado")
    return insumo