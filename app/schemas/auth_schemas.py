from pydantic import BaseModel, EmailStr
from app.core.type_password import PasswordStr

class UserRecoveryPassword(BaseModel):
    email: EmailStr

class UserChangePassword(BaseModel):
    token: str
    senha: PasswordStr
    senha_confirmacao: PasswordStr
