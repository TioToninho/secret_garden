from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from src.secret_garden.database.config import get_db
from src.secret_garden.database.models import Owner
from src.secret_garden.models.owner import (OwnerCreate, OwnerResponse,
                                            OwnerUpdate)

router = APIRouter(
    prefix='/api/owners',
    tags=['owners'],
    responses={404: {'description': 'Not found'}},
)


def owner_to_dict(owner: Any) -> Dict[str, Any]:
    """
    Converte um objeto Owner do SQLAlchemy em um dicionário para validação Pydantic
    """
    return {
        'id': owner.id,
        'name': owner.name,
        'created_at': owner.created_at or datetime.now(),
        'updated_at': owner.updated_at,
    }


@router.post('/', response_model=OwnerResponse)
async def create_owner(owner: OwnerCreate, db: Session = Depends(get_db)):
    """
    Cria um novo proprietário
    """
    try:
        db_owner = Owner(name=owner.name)
        db.add(db_owner)
        db.commit()
        db.refresh(db_owner)
        return {'data': owner_to_dict(db_owner), 'error': None}
    except Exception as e:
        db.rollback()
        return {'data': None, 'error': str(e)}


@router.get('/', response_model=OwnerResponse)
async def get_all_owners(db: Session = Depends(get_db)):
    """
    Retorna todos os proprietários
    """
    try:
        owners = db.query(Owner).all()
        owners_list = [owner_to_dict(owner) for owner in owners]
        return {'data': owners_list, 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.get('/{owner_id}', response_model=OwnerResponse)
async def get_owner(
    owner_id: int = Path(..., title='ID do proprietário', gt=0),
    db: Session = Depends(get_db),
):
    """
    Retorna um proprietário específico pelo ID
    """
    try:
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if owner is None:
            return {
                'data': None,
                'error': f'Proprietário com ID {owner_id} não encontrado',
            }
        return {'data': owner_to_dict(owner), 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.put('/{owner_id}', response_model=OwnerResponse)
async def update_owner(
    owner_update: OwnerUpdate,
    owner_id: int = Path(..., title='ID do proprietário', gt=0),
    db: Session = Depends(get_db),
):
    """
    Atualiza um proprietário existente

    O campo updated_at será atualizado automaticamente com a data/hora atual.
    """
    try:
        db_owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if db_owner is None:
            return {
                'data': None,
                'error': f'Proprietário com ID {owner_id} não encontrado',
            }

        if owner_update.name is not None:
            db_owner.name = owner_update.name

        # Não é necessário atualizar manualmente o campo updated_at
        # SQLAlchemy fará isso automaticamente devido ao parâmetro onupdate=datetime.now

        db.commit()
        db.refresh(db_owner)

        # Confirma que o campo updated_at foi atualizado
        return {'data': owner_to_dict(db_owner), 'error': None}
    except Exception as e:
        db.rollback()
        return {'data': None, 'error': str(e)}


@router.delete('/{owner_id}', response_model=OwnerResponse)
async def delete_owner(
    owner_id: int = Path(..., title='ID do proprietário', gt=0),
    db: Session = Depends(get_db),
):
    """
    Remove um proprietário
    """
    try:
        db_owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if db_owner is None:
            return {
                'data': None,
                'error': f'Proprietário com ID {owner_id} não encontrado',
            }

        # Verificar se existem clientes associados
        clients_count = (
            db.query(Owner)
            .join(Owner.clients)
            .filter(Owner.id == owner_id)
            .count()
        )

        if clients_count > 0:
            return {
                'data': None,
                'error': (
                    f'Não é possível excluir o proprietário com ID {owner_id}. '
                    f'Existem {clients_count} clientes associados.'
                ),
            }

        db.delete(db_owner)
        db.commit()
        return {'data': 'Proprietário removido com sucesso', 'error': None}
    except Exception as e:
        db.rollback()
        return {'data': None, 'error': str(e)}


@router.get('/{owner_id}/clients', response_model=OwnerResponse)
async def get_owner_clients(
    owner_id: int = Path(..., title='ID do proprietário', gt=0),
    db: Session = Depends(get_db),
):
    """
    Retorna a lista de clientes (ID e nome) de um proprietário específico.
    """
    try:
        # Verificar se o proprietário existe
        owner = db.query(Owner).filter(Owner.id == owner_id).first()
        if owner is None:
            return {
                'data': None,
                'error': f'Proprietário com ID {owner_id} não encontrado',
            }

        # Buscar apenas clientes ativos
        clients = [
            {'id': client.id, 'name': client.name}
            for client in owner.clients
            if client.is_active
        ]

        return {'data': clients, 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}
