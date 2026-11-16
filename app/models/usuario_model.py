
from app.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, text
from app.models.enums_model import PerfilUsuario
from datetime import datetime, timezone


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)

    perfil = Column(
        Enum(PerfilUsuario, name="perfil_usuario"),
        nullable=False
    )

    token_verificacao = Column(String(255))

    tentativas_login = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0")
    )

    bloqueado_ate = Column(DateTime(timezone=True))

    vezes_bloqueado = Column(
        Integer,
        nullable=False,
        default=0,
        server_default=text("0")
    )

    ativo = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true")
    )

    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()")
    )

    deleted_at = Column(DateTime(timezone=True))
