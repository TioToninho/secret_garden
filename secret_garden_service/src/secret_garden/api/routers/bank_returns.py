from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Path, Query, Body
from sqlalchemy.orm import Session

from src.secret_garden.database.config import get_db
from src.secret_garden.database.models import BankReturn, Client
from src.secret_garden.models.bank_return import (
    BankReturnCreate, BankReturnUpdate, BankReturnResponse
)
from src.secret_garden.services.bank_return_service import BankReturnService

router = APIRouter(
    prefix='/api/bank-returns',
    tags=['bank-returns'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/client/{client_id}/{month}/{year}', response_model=BankReturnResponse)
async def create_or_update_bank_return(
    client_id: int = Path(..., title="ID do cliente", gt=0),
    month: int = Path(..., title="Mês", ge=1, le=12),
    year: int = Path(..., title="Ano", ge=2000, le=2100),
    data: BankReturnUpdate = Body(...),
    db: Session = Depends(get_db),
):
    """
    Cria ou atualiza um retorno bancário para um cliente.
    
    Se já existir um registro para o mesmo cliente/mês/ano, atualiza.
    Caso contrário, cria um novo registro.
    """
    try:
        result = BankReturnService.create_or_update_bank_return(
            db, client_id, month, year, data.model_dump(exclude_unset=True)
        )
        
        if not result:
            return {
                'data': None,
                'error': 'Erro ao criar/atualizar retorno bancário'
            }
            
        return {
            'data': [{
                'id': result.id,
                'client_id': result.client_id,
                'month': result.month,
                'year': result.year,
                'payer_name': result.payer_name,
                'due_date': result.due_date,
                'payment_date': result.payment_date,
                'title_amount': result.title_amount,
                'charged_amount': result.charged_amount,
                'variation_amount': result.variation_amount,
                'created_at': result.created_at,
                'updated_at': result.updated_at
            }],
            'error': None
        }
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.get('/owner/{owner_id}', response_model=BankReturnResponse)
async def get_owner_bank_returns(
    owner_id: int = Path(..., title="ID do proprietário", gt=0),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Ano"),
    db: Session = Depends(get_db),
):
    """
    Retorna os dados de retorno bancário para um proprietário específico.
    
    Inclui:
    - Lista de retornos bancários dos clientes
    - Resumo dos totais (valor do título, valor cobrado, oscilação)
    - Metadados do retorno
    
    Se mês e ano não forem fornecidos, usa o mês e ano atuais.
    """
    result = BankReturnService.get_owner_bank_returns(
        db, owner_id, month, year
    )
    return result 


@router.get('/month/{month}/{year}', response_model=BankReturnResponse)
async def get_monthly_returns(
    month: int = Path(..., title="Mês", ge=1, le=12),
    year: int = Path(..., title="Ano", ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    """
    Retorna todos os retornos bancários de um mês específico.
    
    Inclui:
    - Lista de todos os retornos bancários do mês
    - Resumo dos totais (valor do título, valor cobrado, oscilação)
    - Metadados do retorno
    """
    try:
        # Buscar todos os retornos do mês
        returns = (
            db.query(BankReturn)
            .join(Client)
            .filter(
                BankReturn.month == month,
                BankReturn.year == year,
                Client.is_active.is_(True)
            )
            .all()
        )

        # Lista para armazenar os dados de retorno
        return_items = []
        
        # Variáveis para o resumo
        summary = {
            "total_title_amount": 0,
            "total_charged_amount": 0,
            "total_variation_amount": 0,
            "total_returns": 0
        }

        # Processar cada retorno
        for bank_return in returns:
            client = bank_return.client
            return_item = {
                "id": bank_return.id,
                "client": {
                    "id": client.id,
                    "name": client.name
                },
                "month": month,
                "year": year,
                "payer_name": bank_return.payer_name,
                "due_date": bank_return.due_date,
                "payment_date": bank_return.payment_date,
                "title_amount": bank_return.title_amount,
                "charged_amount": bank_return.charged_amount,
                "variation_amount": bank_return.variation_amount,
                "created_at": bank_return.created_at,
                "updated_at": bank_return.updated_at
            }

            return_items.append(return_item)

            # Atualizar resumo
            summary["total_title_amount"] += (bank_return.title_amount or 0)
            summary["total_charged_amount"] += (bank_return.charged_amount or 0)
            summary["total_variation_amount"] += (bank_return.variation_amount or 0)
            summary["total_returns"] += 1

        return {
            "data": return_items,
            "summary": summary,
            "metadata": {
                "month": month,
                "year": year,
                "generated_at": datetime.now()
            }
        }
    except Exception as e:
        return {'data': None, 'error': str(e)} 