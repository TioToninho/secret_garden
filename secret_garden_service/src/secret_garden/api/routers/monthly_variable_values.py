from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session

from src.secret_garden.database.config import get_db
from src.secret_garden.models.monthly_variable_values import (
    MonthlyVariableValuesCreate,
    MonthlyVariableValuesUpdate,
    MonthlyVariableValuesResponse
)
from src.secret_garden.services.monthly_variable_values_service import \
    MonthlyVariableValuesService

router = APIRouter(
    prefix='/api/monthly-variable-values',
    tags=['monthly-variable-values'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/', response_model=MonthlyVariableValuesResponse)
async def get_monthly_values(
    client_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Ano"),
    db: Session = Depends(get_db),
):
    """
    Retorna os valores variáveis mensais com base nos filtros fornecidos.
    
    Pode filtrar por cliente_id, mês e ano.
    """
    try:
        results = MonthlyVariableValuesService.get_monthly_values(
            db, client_id=client_id, month=month, year=year
        )

        if not results:
            return {'data': [], 'error': None}

        # Converter objetos SQLAlchemy em dicionários
        values_list = [
            MonthlyVariableValuesService.monthly_values_to_dict(value)
            for value in results
        ]

        return {'data': values_list, 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.get('/client/{client_id}', response_model=MonthlyVariableValuesResponse)
async def get_monthly_values_by_client(
    client_id: int = Path(..., title="ID do cliente", gt=0),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Ano"),
    db: Session = Depends(get_db),
):
    """
    Retorna todos os valores variáveis mensais de um cliente específico.
    
    Opcionalmente pode filtrar por mês e ano.
    """
    try:
        results = MonthlyVariableValuesService.get_monthly_values(
            db, client_id=client_id, month=month, year=year
        )

        if not results:
            return {'data': [], 'error': None}

        # Converter objetos SQLAlchemy em dicionários
        values_list = [
            MonthlyVariableValuesService.monthly_values_to_dict(value)
            for value in results
        ]

        return {'data': values_list, 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.post('/', response_model=MonthlyVariableValuesResponse)
async def create_monthly_values(
    monthly_values: MonthlyVariableValuesCreate = Body(...),
    db: Session = Depends(get_db),
):
    """
    Cria ou atualiza valores variáveis mensais para um cliente.
    
    Se já existir um registro para o mesmo cliente/mês/ano, atualiza.
    Caso contrário, cria um novo registro.
    """
    try:
        result = MonthlyVariableValuesService.create_or_update_monthly_values(
            db, monthly_values
        )
        
        if not result:
            return {
                'data': None,
                'error': 'Erro ao criar/atualizar valores variáveis mensais'
            }
            
        # Envolver o resultado em uma lista para atender ao modelo de resposta
        return {
            'data': [MonthlyVariableValuesService.monthly_values_to_dict(result)],
            'error': None
        }
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.put('/{client_id}/{month}/{year}', response_model=MonthlyVariableValuesResponse)
async def update_monthly_values(
    client_id: int = Path(..., title="ID do cliente", gt=0),
    month: int = Path(..., title="Mês", ge=1, le=12),
    year: int = Path(..., title="Ano", ge=2000, le=2100),
    monthly_values: MonthlyVariableValuesUpdate = Body(...),
    db: Session = Depends(get_db),
):
    """
    Atualiza valores variáveis mensais de um cliente.
    """
    try:
        result = MonthlyVariableValuesService.update_monthly_values(
            db, client_id, month, year, monthly_values
        )
        
        if not result:
            return {
                'data': None,
                'error': (
                    f'Valores variáveis mensais não encontrados para o cliente '
                    f'{client_id} no mês {month}/{year}'
                )
            }
            
        # Envolver o resultado em uma lista para atender ao modelo de resposta
        return {
            'data': [MonthlyVariableValuesService.monthly_values_to_dict(result)],
            'error': None
        }
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.delete('/{client_id}/{month}/{year}', response_model=MonthlyVariableValuesResponse)
async def delete_monthly_values(
    client_id: int = Path(..., title="ID do cliente", gt=0),
    month: int = Path(..., title="Mês", ge=1, le=12),
    year: int = Path(..., title="Ano", ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    """
    Remove valores variáveis mensais de um cliente.
    """
    try:
        success = MonthlyVariableValuesService.delete_monthly_values(
            db, client_id, month, year
        )
        
        if not success:
            return {
                'data': None,
                'error': (
                    f'Valores variáveis mensais não encontrados para o cliente '
                    f'{client_id} no mês {month}/{year}'
                )
            }
            
        # Usar uma lista para o campo data, como exigido pelo modelo de resposta
        return {'data': ['Valores variáveis mensais removidos com sucesso'], 'error': None}
    except Exception as e:
        return {'data': None, 'error': str(e)}


@router.get('/pending', response_model=MonthlyVariableValuesResponse)
async def check_pending_values(
    month: Optional[int] = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Ano"),
    db: Session = Depends(get_db),
):
    """
    Verifica e cria registros mensais pendentes para clientes com variação mensal.
    
    Esta rota executa as seguintes ações:
    1. Verifica todos os clientes ativos com variação mensal (has_monthly_variation=True)
    2. Para cada cliente, verifica se já existe um registro para o mês/ano informado
    3. Se não existir, cria um registro vazio para o cliente
    4. Retorna a lista de clientes que precisam ter seus dados preenchidos
    
    Se mês/ano não forem informados, usa o mês e ano atual.
    """
    try:
        # Verificar e criar valores pendentes
        pending_clients = MonthlyVariableValuesService.check_and_create_pending_values(
            db, current_month=month, current_year=year
        )
        
        if not pending_clients:
            return {
                'data': [],
                'error': 'Todos os clientes estão com dados completos para este mês'
            }
        
        # Preparar mensagem informativa
        mes_atual = month or datetime.now().month
        ano_atual = year or datetime.now().year
        total_pendentes = len(pending_clients)
        
        for client in pending_clients:
            # Adiciona traduções para facilitar leitura na interface
            translated_fields = []
            for field in client.get('empty_fields', []):
                if field == "water_bill":
                    translated_fields.append("Water Bill")
                elif field == "gas_bill":
                    translated_fields.append("Gas Bill")
                elif field == "insurance":
                    translated_fields.append("Insurance")
                elif field == "property_tax":
                    translated_fields.append("Property Tax")
                elif field == "condo_fee":
                    translated_fields.append("Condo Fee")
            
            client['pending_fields'] = translated_fields
            
        return {
            'data': pending_clients,
            'error': None
        }
    except Exception as e:
        return {'data': None, 'error': str(e)} 