from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# AJUSTE: caminhos reais no seu projeto
from app.database.database import get_db
from app.models.usuario_model import Usuario
from app.models.restaurante_usuario_model import RestauranteUsuario
from app.middlewares.auth import autorizar_perfis


def get_restaurante_id(
    usuario: dict = Depends(autorizar_perfis("admin", "user")),
    db: Session = Depends(get_db),
) -> int:
    usuario_db = db.query(Usuario).filter(Usuario.email == usuario.get("sub")).first()
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
    return vinculo.restaurante_id