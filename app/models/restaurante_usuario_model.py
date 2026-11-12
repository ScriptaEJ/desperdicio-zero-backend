# app/models/restaurante_usuario.py

from app.database.database import Base
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid


class RestauranteUsuario(Base):
    __tablename__ = "restaurante_usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurantes.id"),
        nullable=False
    )
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("restaurante_id", "usuario_id"),
    )