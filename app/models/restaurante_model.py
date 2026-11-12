# app/models/restaurante.py

from app.database.database import Base
from sqlalchemy import Column, String, Numeric, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Restaurante(Base):
    __tablename__ = "restaurantes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(150), nullable=False)
    cwid = Column(String(100))
    custo_medio_kg = Column(
        Numeric(12, 2),
        nullable=False,
        server_default=text("0")
    )
    criado_em = Column(DateTime(timezone=True))