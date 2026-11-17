
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.insumo_model import Insumo
from app.schemas.insumos_schemas import CreateInsumo, UpdateInsumo
from exceptions.exceptions import InsumoNaoEncontrado, DadosInvalidosInsumo



def criar_insumo(data: CreateInsumo, db: Session):
   
    if not data.restaurante_id:
        raise DadosInvalidosInsumo("ID do restaurante é obrigatório")

    if not isinstance(data.restaurante_id, UUID):
        raise DadosInvalidosInsumo("ID do restaurante deve ser um UUID válido")
    
    insumo = Insumo(**data.model_dump())

    db.add(insumo)
    db.commit()
    db.refresh(insumo)

    return insumo


def listar_insumos(restaurante_id: UUID, db: Session):
    
    if not restaurante_id:
        raise DadosInvalidosInsumo("ID do restaurante é obrigatório")

    if not isinstance(restaurante_id, UUID):
        raise DadosInvalidosInsumo("ID do restaurante deve ser um UUID válido")

    if not db.query(Insumo).filter(Insumo.restaurante_id == restaurante_id).first():
        raise InsumoNaoEncontrado("Nenhum insumo encontrado para o restaurante especificado")
    
    return (
        db.query(Insumo)
        .filter(Insumo.restaurante_id == restaurante_id)
        .all()
    )


def buscar_insumo(insumo_id: UUID, db: Session):
    if not insumo_id:
        raise DadosInvalidosInsumo("ID do insumo é obrigatório")

    if not isinstance(insumo_id, UUID):
        raise DadosInvalidosInsumo("ID do insumo deve ser um UUID válido")

    if not db.query(Insumo).filter(Insumo.id == insumo_id).first():
        raise InsumoNaoEncontrado("Insumo não encontrado")
    
    insumo = (
        db.query(Insumo)
        .filter(Insumo.id == insumo_id)
        .first()
    )

    return insumo


def atualizar_insumo(insumo_id: UUID, data: UpdateInsumo, db: Session):
    if not insumo_id:
        raise DadosInvalidosInsumo("ID do insumo é obrigatório")

    if not isinstance(insumo_id, UUID):
        raise DadosInvalidosInsumo("ID do insumo deve ser um UUID válido")

    if not db.query(Insumo).filter(Insumo.id == insumo_id).first():
        raise InsumoNaoEncontrado("Insumo não encontrado")
    
    insumo = buscar_insumo(insumo_id, db)

    dados = data.model_dump(exclude_unset=True)

    for campo, valor in dados.items():
        setattr(insumo, campo, valor)

    db.commit()
    db.refresh(insumo)

    return insumo


def deletar_insumo(insumo_id: UUID, db: Session):
    if not isinstance(insumo_id, UUID):
        raise DadosInvalidosInsumo("ID do insumo deve ser um UUID válido")

    if not db.query(Insumo).filter(Insumo.id == insumo_id).first():
        raise InsumoNaoEncontrado("Insumo não encontrado")
    
    insumo = buscar_insumo(insumo_id, db)

    insumo.ativo = False

    db.commit()
    db.refresh(insumo)

    return insumo
