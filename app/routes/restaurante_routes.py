from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.middlewares.auth import autorizar_perfis
from app.database.database import get_db
from app.schemas.restaurante_schema import (
    RestauranteResponse,
    RestaurantesPaginados,
    UpdateRestaurante,
    createRestaurante,
)
from app.exceptions.exceptions import RestauranteNaoEncontrado
from app.services.restaurante_services import (
    create_restaurante,
    delete_restaurante,
    get_restaurante_by_id,
    get_restaurantes_paginated,
    update_restaurante,
)
from app.models.usuario_model import Usuario
router = APIRouter(prefix="/restaurantes", tags=["Restaurantes"])

@router.post("/", response_model=RestauranteResponse, status_code=201)
def criar_restaurante(
    data: createRestaurante,
    usuario: dict = Depends(autorizar_perfis("admin", "user")),
    db: Session = Depends(get_db),
):
    usuario_db = db.query(Usuario).filter(Usuario.email == usuario.get("sub")).first()
    if not usuario_db:
        raise HTTPException(status_code=401, detail="Usuário autenticado não encontrado")

    return create_restaurante(db, data, usuario_db.id)

@router.get("/{restaurante_id}", response_model=RestauranteResponse, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def get_restaurante_endpoint(
    restaurante_id: int, db: Session = Depends(get_db)
):
    restaurante = get_restaurante_by_id(db, restaurante_id)
    if not restaurante:
        raise RestauranteNaoEncontrado
    return restaurante

@router.get("/", response_model=RestaurantesPaginados, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def get_restaurantes_paginated_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    return get_restaurantes_paginated(db, page, size)

@router.put("/{restaurante_id}", response_model=RestauranteResponse, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def update_restaurante_endpoint(
    restaurante_id: int,
    restaurante_update: UpdateRestaurante,
    db: Session = Depends(get_db)
):
    updated_restaurante = update_restaurante(db, restaurante_id, restaurante_update)
    if not updated_restaurante:
        raise RestauranteNaoEncontrado
    return updated_restaurante

@router.delete("/{restaurante_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(autorizar_perfis("admin", "user"))])
def delete_restaurante_endpoint(
    restaurante_id: int, db: Session = Depends(get_db)
):
    success = delete_restaurante(db, restaurante_id)
    if not success:
        raise RestauranteNaoEncontrado
    return None