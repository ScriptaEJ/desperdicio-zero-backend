

from math import ceil
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.perda_model import Perda
from app.schemas.perda_schemas import CreatePerda, UpdatePerda
from app.exceptions.exceptions import (
    PerdaNaoEncontrada,
    PerdaDadosInvalidos
)



def criar_perda(
    data: CreatePerda,
    usuario_id: int,
    db: Session
):
    if data.quantidade <= 0:
        raise PerdaDadosInvalidos(
            "A quantidade deve ser maior que zero."
        )

    if data.custo_unitario <= 0:
        raise PerdaDadosInvalidos(
            "O custo unitário deve ser maior que zero."
        )

    dados = data.model_dump()

    dados["usuario_id"] = usuario_id

    dados["valor_total"] = (
        Decimal(str(data.quantidade)) *
        Decimal(str(data.custo_unitario))
    )

    perda = Perda(**dados)

    db.add(perda)
    db.commit()
    db.refresh(perda)

    return perda



def listar_perdas(
    page: int,
    size: int,
    db: Session
):
    query = db.query(Perda)

    total = query.count()

    perdas = (
        query
        .order_by(Perda.data_perda.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": ceil(total / size) if total else 0,
        "items": perdas
    }


def buscar_perda(
    perda_id: UUID,
    db: Session
):
    perda = db.query(Perda).filter(
        Perda.id == perda_id
    ).first()

    if not perda:
        raise PerdaNaoEncontrada()

    return perda


def atualizar_perda(
    perda_id: UUID,
    data: UpdatePerda,
    db: Session
):
    perda = buscar_perda(perda_id, db)

    dados = data.model_dump(exclude_unset=True)

    for campo, valor in dados.items():
        setattr(perda, campo, valor)

    if perda.quantidade <= 0:
        raise PerdaDadosInvalidos(
            "A quantidade deve ser maior que zero."
        )

    if perda.custo_unitario <= 0:
        raise PerdaDadosInvalidos(
            "O custo unitário deve ser maior que zero."
        )

    perda.valor_total = (
        Decimal(str(perda.quantidade)) *
        Decimal(str(perda.custo_unitario))
    )

    db.commit()
    db.refresh(perda)

    return perda


def excluir_perda(
    perda_id: UUID,
    db: Session
):
    perda = buscar_perda(perda_id, db)

    db.delete(perda)
    db.commit()

    return {
        "mensagem": "Perda excluída com sucesso"
    }
