from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from src.secret_garden.database.config import get_db
from src.secret_garden.database.models import MonthlyCalculation, Client
from src.secret_garden.models.monthly_calculation import (
    MonthlyCalculationResponse, MonthlyCalculationSummary)
from src.secret_garden.services.monthly_calculation_service import \
    MonthlyCalculationService

router = APIRouter(
    prefix='/api/monthly-calculations',
    tags=['monthly-calculations'],
    responses={404: {'description': 'Not found'}},
)


def calculation_to_dict(calculation: Any) -> Dict[str, Any]:
    """
    Converte um objeto MonthlyCalculation do SQLAlchemy em um dicionário
    para validação Pydantic
    """
    return {
        'id': calculation.id,
        'client_id': calculation.client_id,
        'month': calculation.month,
        'year': calculation.year,
        'rent_amount': calculation.rent_amount,
        'calculation_base': calculation.calculation_base,
        'tenant_payment': calculation.tenant_payment,
        'commission': calculation.commission,
        'deposit_amount': calculation.deposit_amount,
        'created_at': calculation.created_at or datetime.now(),
        'updated_at': calculation.updated_at,
    }


@router.post('/calculate', response_model=MonthlyCalculationSummary)
async def calculate_monthly_values(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    """
    Calcula os valores financeiros mensais para todos os clientes ativos.

    Se mês e ano não forem fornecidos, usa o mês e ano atuais.

    Retorna um resumo do processamento com contagem de sucessos e falhas.
    """
    try:
        result = await MonthlyCalculationService.calculate_for_all_clients(
            db, month, year
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Erro ao calcular valores mensais: {str(e)}',
        )


@router.get('/', response_model=MonthlyCalculationResponse)
async def get_monthly_calculations(
    client_id: Optional[int] = None,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    """
    Retorna os cálculos mensais com base nos filtros fornecidos.

    Pode filtrar por cliente_id, mês e ano.
    """
    try:
        query = db.query(MonthlyCalculation)

        if client_id:
            query = query.filter(MonthlyCalculation.client_id == client_id)
        if month:
            query = query.filter(MonthlyCalculation.month == month)
        if year:
            query = query.filter(MonthlyCalculation.year == year)

        results = query.all()

        if not results:
            return {'data': [], 'error': None}

        # Converter objetos SQLAlchemy em dicionários para validação Pydantic
        calculations_list = [calculation_to_dict(calc) for calc in results]

        return {'data': calculations_list, 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.get('/client/{client_id}', response_model=MonthlyCalculationResponse)
async def get_calculations_by_client(
    client_id: int = Path(..., title="ID do cliente", gt=0),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    """
    Retorna todos os cálculos mensais de um cliente específico.
    
    Opcionalmente pode filtrar por mês e ano.
    """
    try:
        # Verificar se o cliente existe
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {
                'data': None, 
                'error': f'Cliente com ID {client_id} não encontrado'
            }
        
        # Consultar os cálculos mensais
        query = db.query(MonthlyCalculation).filter(
            MonthlyCalculation.client_id == client_id
        )
        
        # Aplicar filtros adicionais
        if month:
            query = query.filter(MonthlyCalculation.month == month)
        if year:
            query = query.filter(MonthlyCalculation.year == year)
        
        results = query.all()
        
        if not results:
            return {'data': [], 'error': None}
        
        # Converter objetos SQLAlchemy em dicionários
        calculations_list = [calculation_to_dict(calc) for calc in results]
        
        return {'data': calculations_list, 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.get('/owner/{owner_id}', response_model=MonthlyCalculationResponse)
async def get_calculations_by_owner(
    owner_id: int = Path(..., title="ID do proprietário", gt=0),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    """
    Retorna todos os cálculos mensais relacionados aos clientes de um proprietário.
    
    Opcionalmente pode filtrar por mês e ano.
    """
    try:
        # Primeiro, encontrar todos os clientes deste proprietário
        clients = db.query(Client).filter(Client.owner_id == owner_id).all()
        
        if not clients:
            return {
                'data': None, 
                'error': (
                    f'Nenhum cliente encontrado para o proprietário com ID {owner_id}'
                )
            }
        
        # Obter os IDs dos clientes
        client_ids = [client.id for client in clients]
        
        # Buscar cálculos mensais para estes clientes
        query = db.query(MonthlyCalculation).filter(
            MonthlyCalculation.client_id.in_(client_ids)
        )
        
        # Aplicar filtros adicionais
        if month:
            query = query.filter(MonthlyCalculation.month == month)
        if year:
            query = query.filter(MonthlyCalculation.year == year)
        
        results = query.all()
        
        if not results:
            return {'data': [], 'error': None}
        
        # Converter objetos SQLAlchemy em dicionários
        calculations_list = [calculation_to_dict(calc) for calc in results]
        
        return {'data': calculations_list, 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}
