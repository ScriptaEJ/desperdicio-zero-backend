
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Literal
from datetime import datetime

from app.core.type_password import PasswordStr

Perfil = Literal["user", "admin"]


class CreateUsuario(BaseModel):
    nome: str
    email: EmailStr
    senha: PasswordStr
    perfil: Perfil


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    perfil: Perfil
    ativo: bool
    criado_em: datetime


class UsuariosPaginados(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    items: list[UsuarioResponse]


class UpdateUser(BaseModel):
    email: EmailStr | None = None
    nome: str | None = None
    perfil: Perfil | None = None


class LoginUsuario(BaseModel):
    email: EmailStr
    senha: PasswordStr