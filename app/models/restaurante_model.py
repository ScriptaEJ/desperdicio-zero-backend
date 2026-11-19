# app/models/restaurante.py

from app.database.database import Base
from sqlalchemy import Column, String, Numeric, DateTime, text, Integer
from sqlalchemy.dialects.postgresql import UUID


class Restaurante(Base):
    __tablename__ = "restaurantes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    cwid = Column(String(100))
    custo_medio_kg = Column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0")
    )
    criado_em = Column(DateTime(timezone=True))