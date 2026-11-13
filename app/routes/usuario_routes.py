from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.middlewares.auth import autorizar_perfis, get_current_user
from app.schemas.usuario_schema import CreateUsuario, UsuariosPaginados, UsuarioResponse, UpdateUser, LoginUsuario
from app.services.usuario_services import *

user_routes = APIRouter(tags=["03. Users"])

#------------------- Rota de Login ---------------------------


@user_routes.post("/login")
def login(
    data: LoginUsuario,
    db: Session = Depends(get_db),
):
    return login_user(data, db)


#------------------- Rotas do Usuario -------------------------
@user_routes.post("/users", status_code=201)
def create_user(
    data: CreateUsuario,
    db: Session = Depends(get_db),
):
    register_user(data, db)
    return {"message": "Conta criada com sucesso"}

@user_routes.get("/users", response_model=UsuariosPaginados, dependencies=[Depends(autorizar_perfis("user"))])
def listar_user(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return listar_users(db, page, size)


@user_routes.get("/users/{id}", response_model=UsuarioResponse, dependencies=[Depends(autorizar_perfis("user"))])
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
):
    return get_user_id(id, db)


@user_routes.patch("/user/{id}", response_model=UsuarioResponse, dependencies=[Depends(autorizar_perfis("user"))])
def update_user_by_id(
    id: int,
    data: UpdateUser,
    db: Session = Depends(get_db),
):
    return update_user(id, data, db)


@user_routes.delete("/user/{id}", dependencies=[Depends(autorizar_perfis("user"))])
def delete_user_by_id(
    id: int,
    db: Session = Depends(get_db),
):
    return delete_user(id, db)