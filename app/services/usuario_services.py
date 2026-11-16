
from math import ceil
from jose import jwt

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash

from app.middlewares.auth import SECRET, ALGORITHM
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UpdateUser
from app.exceptions.exceptions import (
    DadosInvalidos,
    ContaExistente,
    UserNotFound,
    DesactivatedUser,
)


# Login
def login_user(data, db: Session):
    email = data.email.strip().lower()

    user = db.query(Usuario).filter(Usuario.email == email).first()

    if not user:
        raise DadosInvalidos()

    if not user.ativo:
        raise DesactivatedUser()

    if not check_password_hash(user.senha, data.senha):
        raise DadosInvalidos()

    payload = {
        "sub": user.email,
        "perfil": user.perfil,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# Cadastro
def register_user(data, db: Session):
    email = data.email.strip().lower()
    senha = data.senha
    nome = data.nome
    perfil = data.perfil

    if not email or not senha or not nome or not perfil:
        raise DadosInvalidos()

    user = db.query(Usuario).filter(Usuario.email == email).first()

    if user:
        raise ContaExistente()

    senha_hash = generate_password_hash(senha)

    novo_user = Usuario(
        email=email,
        senha=senha_hash,
        nome=nome,
        perfil=perfil,
        ativo=True,
    )

    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    return novo_user


# Listagem
def listar_users(db: Session, page: int, size: int):
    total = db.query(Usuario).count()

    dados = (
        db.query(Usuario)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": ceil(total / size) if total > 0 else 1,
        "items": dados
    }


# Buscar usuário por ID
def get_user_id(id: int, db: Session):
    user = db.query(Usuario).filter(Usuario.id == id).first()

    if not user:
        raise UserNotFound()

    return user


# Atualizar usuário
def update_user(id: int, data: UpdateUser, db: Session):
    user = get_user_id(id, db)

    dados_atualizados = {
        campo: valor
        for campo, valor in data.model_dump(exclude_unset=True).items()
        if valor is not None
    }

    for campo, valor in dados_atualizados.items():
        setattr(user, campo, valor)

    db.commit()
    db.refresh(user)

    return user


# Desativar usuário
def delete_user(id: int, db: Session):
    user = get_user_id(id, db)

    user.ativo = False

    db.commit()
    db.refresh(user)

    return user
