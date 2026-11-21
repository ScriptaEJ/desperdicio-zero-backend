
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.restaurante_usuario_model import RestauranteUsuario  # ajuste o caminho
from app.database.database import get_db
from app.middlewares.auth import autorizar_perfis
from app.models.usuario_model import Usuario
from app.dependencies.restaurante_dependency import get_restaurante_id
from app.exceptions.exceptions import PerdaNaoEncontrada
from app.schemas.perda_schemas import (
    CreatePerda,
    UpdatePerda,
    PerdaResponse,
    PerdasPaginadas
)

from app.services.perda_services import (
    criar_perda,
    listar_perdas,
    buscar_perda,
    atualizar_perda,
    excluir_perda
)

perda_router = APIRouter(tags=["05. Perdas"])

@perda_router.post("/perdas", response_model=PerdaResponse, status_code=201)
def registrar_perda(
    data: CreatePerda,
    usuario: dict = Depends(autorizar_perfis("admin", "user")),
    db: Session = Depends(get_db),
):
    email = usuario.get("sub")

    usuario_db = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario_db:
        raise HTTPException(status_code=401, detail="Usuário autenticado não encontrado")

    vinculo = (
        db.query(RestauranteUsuario)
        .filter(RestauranteUsuario.usuario_id == usuario_db.id)
        .first()
    )
    if not vinculo:
        raise HTTPException(
            status_code=403,
            detail="Usuário não está vinculado a nenhum restaurante",
        )

    return criar_perda(data, usuario_db.id, vinculo.restaurante_id, db)



@perda_router.get(
    "/perdas",
    response_model=PerdasPaginadas
)
def listar_registros_perda(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    restaurante_id: int = Depends(get_restaurante_id),
    db: Session = Depends(get_db)
):
    return listar_perdas(page, size, restaurante_id, db)


@perda_router.get(
    "/perdas/{perda_id}",
    response_model=PerdaResponse
)
def obter_perda(
    perda_id: int,
    usuario: Usuario = Depends(
        autorizar_perfis("admin", "user")
    ),
    db: Session = Depends(get_db)
):
    try:
        return buscar_perda(perda_id, usuario.id, db)

    except PerdaNaoEncontrada:
        raise HTTPException(
            status_code=404,
            detail="Registro de perda não encontrado"
        )


@perda_router.patch(
    "/perdas/{perda_id}",
    response_model=PerdaResponse
)
def editar_perda(
    perda_id: int,
    data: UpdatePerda,
    usuario: Usuario = Depends(
        autorizar_perfis("admin", "user")
    ),
    db: Session = Depends(get_db)
):
    try:
        return atualizar_perda(
            perda_id,
            data,
            usuario.id,
            db
        )

    except PerdaNaoEncontrada:
        raise HTTPException(
            status_code=404,
            detail="Registro de perda não encontrado"
        )


@perda_router.delete("/perdas/{perda_id}")
def remover_perda(
    perda_id: int,
    usuario: Usuario = Depends(
        autorizar_perfis("admin", "user")
    ),
    db: Session = Depends(get_db)
):
    try:
        return excluir_perda(perda_id, usuario.id, db)

    except PerdaNaoEncontrada:
        raise HTTPException(
            status_code=404,
            detail="Registro de perda não encontrado"
        )
