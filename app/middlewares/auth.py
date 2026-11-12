from jose import jwt, JWTError
from fastapi import status, Depends
from dotenv import load_dotenv
from typing import Literal
import os
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.usuario_model import Usuario
from app.exceptions.exceptions import TokenNaoAutenticado, UsuarioNaoAutorizado
from app.exceptions.exceptions import UserNotFound, DesactivatedUser

load_dotenv()

SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")
security = HTTPBearer()

Perfil = Literal["user"]

# ----------------------- AUTENTICAÇÃO -----------------------

def autentica(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise TokenNaoAutenticado()

# ----------------------- AUTORIZAÇÃO -----------------------

def autorizar_perfis(*perfis_permitidos: Perfil):
    def verificar(credenciais: HTTPAuthorizationCredentials = Depends(security)):
        
        usuario = autentica(credenciais.credentials)

        if usuario.get("perfil") not in perfis_permitidos:
            raise UsuarioNaoAutorizado()

        return usuario
    return verificar

# ----------------------- USUARIO ATUAL PELO TOKEN -----------------------

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials

    payload = autentica(token)

    user = db.query(Usuario).filter(
        Usuario.email == payload["sub"]
    ).first()

    if not user:
        raise UserNotFound()

    if not user.ativo:
        raise DesactivatedUser()

    return payload