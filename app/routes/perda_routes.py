
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.middlewares.auth import autorizar_perfis
from app.models.usuario_model import Usuario

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
    excluir_perda,
    PerdaNaoEncontrada
)


perda_router = APIRouter(tags=["05. Perdas"])



@perda_router.post(
    "/perdas",
    response_model=PerdaResponse,
    status_code=201
)
def registrar_perda(
    data: CreatePerda,
    usuario: dict = Depends(autorizar_perfis("admin", "user")),
    db: Session = Depends(get_db)
):
    email = usuario.get("sub")

    usuario_db = db.query(Usuario).filter(
        Usuario.email == email
    ).first()

    if not usuario_db:
        raise HTTPException(
            status_code=401,
            detail="Usuário autenticado não encontrado"
        )

    return criar_perda(data, usuario_db.id, db)



@perda_router.get(
    "/perdas",
    response_model=PerdasPaginadas,
    dependencies=[Depends(autorizar_perfis("admin", "user"))]
)
def listar_registros_perda(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return listar_perdas(page, size, db)


@perda_router.get(
    "/perdas/{perda_id}",
    response_model=PerdaResponse,
    dependencies=[Depends(autorizar_perfis("admin", "user"))]
)
def obter_perda(
    perda_id: int,
    db: Session = Depends(get_db)
):
    try:
        return buscar_perda(perda_id, db)

    except PerdaNaoEncontrada:
        raise HTTPException(
            status_code=404,
            detail="Registro de perda não encontrado"
        )


@perda_router.patch(
    "/perdas/{perda_id}",
    response_model=PerdaResponse,
    dependencies=[Depends(autorizar_perfis("admin", "user"))]
)
def editar_perda(
    perda_id: int,
    data: UpdatePerda,
    db: Session = Depends(get_db)
):
    try:
        return atualizar_perda(perda_id, data, db)

    except PerdaNaoEncontrada:
        raise HTTPException(
            status_code=404,
            detail="Registro de perda não encontrado"
        )


@perda_router.delete(
    "/perdas/{perda_id}",
    dependencies=[Depends(autorizar_perfis("admin", "user"))]
)
def remover_perda(
    perda_id: int,
    db: Session = Depends(get_db)
):
    try:
        return excluir_perda(perda_id, db)

    except PerdaNaoEncontrada:
        raise HTTPException(
            status_code=404,
            detail="Registro de perda não encontrado"
        )
