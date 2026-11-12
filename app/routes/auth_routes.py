from fastapi import APIRouter
from app.core.limiter import limiter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from app.database.database import get_db
from app.middlewares.auth import autorizar_perfis, get_current_user
from fastapi import Request
from fastapi import HTTPException
from app.services.auth_services import validar_token_recuperacao_senha
from app.schemas.auth_schemas import UserRecoveryPassword, UserChangePassword
from app.models.usuario_model import Usuario
from app.services.auth_services import criar_token_recuperacao_senha, enviar_email
from werkzeug.security import generate_password_hash
from app.exceptions.exceptions import UserNotFound, DistinctPasswords

auth_routes = APIRouter(prefix="/auth", tags=["01. Auth"])

# ------------------------- RECUPERAR SENHA -------------------------

@auth_routes.post("/recovery-password", status_code=200)
@limiter.limit("3/minute")  
def recovery_password(request: Request, payload: UserRecoveryPassword, db: Session = Depends(get_db)):
        
    email = payload.email

    user = db.query(Usuario).filter(Usuario.email == email).first()

    if not user:
        raise UserNotFound()
    
    token = criar_token_recuperacao_senha(user.email)

    link = f"{os.getenv('BASE_URL')}/change-password?token={token}"

    html = f"""
        <h2>Email para troca de senha.</h2>
        <p>Clique no link abaixo:</p>
        <a href="{link}">Alterar senha</a>
        <p>Se não houve tentativa de alteração de senha, por favor ignore este email.</p>
    """

    enviar_email(destinatario=user.email, assunto="Alteração de senha.", html_content=html)

    return {"message": "Se o email existir no sistema, você recebrá instruções no seu email."}
    
# ------------------------- REDEFINIR SENHA -------------------------

@auth_routes.post("/change-password", status_code=200)
@limiter.limit("3/minute")  
def change_password(request: Request, payload: UserChangePassword, db: Session = Depends(get_db)):
        
    senha = payload.senha
    senha_confirmacao = payload.senha_confirmacao
    token = payload.token

    if senha != senha_confirmacao:
        raise DistinctPasswords()

    token_decodificado = validar_token_recuperacao_senha(token)

    email = token_decodificado["sub"]

    user = db.query(Usuario).filter(Usuario.email == email).first()

    if not user:
        raise UserNotFound()

    senha_hash = generate_password_hash(senha)

    user.senha_hash = senha_hash
    db.commit()

    return {"message": "Senha atualizada com sucesso."}

