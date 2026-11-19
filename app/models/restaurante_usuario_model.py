# app/models/restaurante_usuario.py

from app.database.database import Base
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint


class RestauranteUsuario(Base):
    __tablename__ = "restaurante_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    restaurante_id = Column(
        Integer,
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