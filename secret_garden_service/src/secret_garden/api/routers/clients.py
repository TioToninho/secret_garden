from datetime import datetime, date
from typing import Any, Dict, Optional, List

from fastapi import (
    APIRouter, Body, Depends, HTTPException, Path, Query, status
)
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta

from src.secret_garden.database.config import get_db
from src.secret_garden.database.models import Client
from src.secret_garden.models.client import (
    AdjustmentResponse, ClientCreate, ClientResponse, ClientUpdate
)
from src.secret_garden.services.client_service import ClientService

router = APIRouter(
    prefix='/api/clients',
    tags=['clients'],
    responses={404: {'description': 'Not found'}},
)


def client_to_dict(client: Any) -> Dict[str, Any]:
    """
    Converte um objeto Cliente do SQLAlchemy em um dicionário 
    para validação Pydantic
    """
    return {
        'id': client.id,
        'name': client.name,
        'owner_id': client.owner_id,
        'status': client.status,
        'due_date': client.due_date,
        'amount_paid': client.amount_paid,
        'property_tax': client.property_tax,
        'interest': client.interest,
        'utilities': client.utilities,
        'insurance': client.insurance,
        'condo_fee': client.condo_fee,
        'percentage': client.percentage,
        'delivery_fee': client.delivery_fee,
        'start_date': client.start_date,
        'condo_paid': client.condo_paid
        if client.condo_paid is not None
        else False,
        'withdrawal_date': client.withdrawal_date,
        'withdrawal_number': client.withdrawal_number,
        'payment_date': client.payment_date,
        'notes': client.notes,
        'has_monthly_variation': client.has_monthly_variation
        if client.has_monthly_variation is not None
        else False,
        'is_active': client.is_active
        if client.is_active is not None
        else True,
        'created_at': client.created_at or datetime.now(),
        'updated_at': client.updated_at,
    }


@router.get('/names', response_model=ClientResponse)
async def list_client_names(
    is_active: Optional[bool] = Query(True, description="Filtrar por clientes ativos"),
    owner_id: Optional[int] = Query(None, description="Filtrar por proprietário"),
    db: Session = Depends(get_db),
):
    """
    Lista apenas os nomes e IDs de todos os clientes.
    
    Retorna uma lista simplificada para uso em dropdowns e seletores.
    Inclui o ID do proprietário para facilitar o agrupamento.
    """
    try:
        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active
        if owner_id is not None:
            filters["owner_id"] = owner_id
            
        clients = ClientService.get_clients(db, filters)
        
        # Criar uma lista simplificada com ID, nome e ID do proprietário
        client_names = [
            {"id": client.id, "name": client.name, "owner_id": client.owner_id} 
            for client in clients
        ]
        
        return {"data": client_names, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.get('/', response_model=ClientResponse, status_code=status.HTTP_200_OK)
async def list_clients(
    is_active: Optional[bool] = Query(
        None, description='Filtrar por clientes ativos'
    ),
    has_monthly_variation: Optional[bool] = Query(
        None, description='Filtrar por variação mensal'
    ),
    owner_id: Optional[int] = Query(
        None, description='Filtrar por ID do proprietário'
    ),
    db: Session = Depends(get_db),
):
    """
    Lista todos os clientes com filtros opcionais
    """
    filters = {}
    if is_active is not None:
        filters['is_active'] = is_active
    if has_monthly_variation is not None:
        filters['has_monthly_variation'] = has_monthly_variation
    if owner_id is not None:
        filters['owner_id'] = owner_id

    try:
        clients = ClientService.get_clients(db, filters)

        # Convertendo objetos SQLAlchemy em dicionários para validação Pydantic
        client_list = [client_to_dict(client) for client in clients]

        return ClientResponse(data=client_list)
    except Exception as e:
        return ClientResponse(error=str(e))


@router.post(
    '/', response_model=ClientResponse, status_code=status.HTTP_201_CREATED
)
async def create_client(
    client_data: ClientCreate = Body(..., description='Dados do cliente'),
    db: Session = Depends(get_db),
):
    """
    Cria um novo cliente
    """
    try:
        client = ClientService.create_client(db, client_data)
        return ClientResponse(data=client_to_dict(client))
    except Exception as e:
        return ClientResponse(error=str(e))


@router.get("/adjustments", response_model=AdjustmentResponse)
async def check_contract_adjustments(
    db: Session = Depends(get_db)
):
    """
    Verifica os contratos que terão reajuste no próximo mês.
    
    Retorna uma lista de contratos que precisam ser reajustados e 
    automaticamente adiciona a marcação "REAJUSTE" nas observações.
    """
    try:
        adjustment_info = ClientService.verificar_reajustes(db)
        return adjustment_info
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao verificar reajustes: {str(e)}"
        )


@router.get("/adjustments/next-3-months", response_model=ClientResponse)
async def get_next_three_months_adjustments(
    db: Session = Depends(get_db)
):
    """
    Lista todos os contratos que terão reajuste nos próximos 3 meses.
    
    Retorna uma lista de clientes com suas datas de reajuste agrupadas por mês.
    """
    try:
        hoje = datetime.now().date()
        
        # Calcular período de 3 meses
        tres_meses_depois = hoje + relativedelta(months=3)
        
        # Buscar todos os clientes ativos com data de início
        clientes = db.query(Client).filter(
            Client.is_active == True,
            Client.start_date.isnot(None)
        ).all()
        
        # Filtrar e processar apenas clientes com reajuste nos próximos 3 meses
        result = []
        
        for cliente in clientes:
            if not cliente.start_date:
                continue
                
            proximo_reajuste = ClientService.calcular_proximo_reajuste(
                cliente.start_date
            )
            
            # Verificar se o reajuste está nos próximos 3 meses
            if (proximo_reajuste and 
                hoje <= proximo_reajuste <= tres_meses_depois):
                
                result.append({
                    "id": cliente.id,
                    "name": cliente.name,
                    "start_date": cliente.start_date.isoformat(),
                    "next_adjustment": proximo_reajuste.isoformat(),
                    "owner_id": cliente.owner_id,
                    "month": proximo_reajuste.month,
                    "year": proximo_reajuste.year
                })
        
        # Agrupar por mês
        result_by_month = {}
        for item in result:
            month_key = f"{item['month']}/{item['year']}"
            if month_key not in result_by_month:
                result_by_month[month_key] = []
            result_by_month[month_key].append(item)
        
        return {"data": result_by_month, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.get("/{client_id}/next-adjustment", response_model=ClientResponse)
async def get_client_next_adjustment(
    client_id: int = Path(..., title="ID do cliente", gt=0),
    db: Session = Depends(get_db)
):
    """
    Verifica a próxima data de reajuste de um cliente específico.
    """
    try:
        # Buscar o cliente
        cliente = ClientService.get_client(db, client_id)
        if not cliente:
            return {"data": None, "error": f"Cliente com ID {client_id} não encontrado"}
        
        # Se o cliente não tiver data de início, não há como calcular reajuste
        if not cliente.start_date:
            return {
                "data": None, 
                "error": f"Cliente com ID {client_id} não possui data de início definida"
            }
        
        # Calcular próximo reajuste
        proximo_reajuste = ClientService.calcular_proximo_reajuste(cliente.start_date)
        
        # Calcular quantos dias faltam
        hoje = datetime.now().date()
        dias_restantes = (proximo_reajuste - hoje).days
        
        result = {
            "id": cliente.id,
            "name": cliente.name,
            "start_date": cliente.start_date.isoformat(),
            "next_adjustment": proximo_reajuste.isoformat(),
            "days_until_adjustment": dias_restantes,
            "owner_id": cliente.owner_id
        }
        
        return {"data": result, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.get(
    '/{client_id}',
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
)
async def get_client(
    client_id: int = Path(..., description='ID do cliente'),
    db: Session = Depends(get_db),
):
    """
    Busca um cliente específico pelo ID
    """
    try:
        client = ClientService.get_client(db, client_id)

        if not client:
            return ClientResponse(
                error=f'Cliente com ID {client_id} não encontrado'
            )

        # Convertendo objeto SQLAlchemy em dicionário para validação Pydantic
        client_dict = client_to_dict(client)

        return ClientResponse(data=client_dict)
    except Exception as e:
        return ClientResponse(error=str(e))


@router.put(
    '/{client_id}',
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
)
async def update_client(
    client_id: int = Path(..., description='ID do cliente'),
    client_data: ClientUpdate = Body(
        ..., description='Dados para atualização'
    ),
    db: Session = Depends(get_db),
):
    """
    Atualiza dados de um cliente existente
    """
    try:
        client = ClientService.update_client(db, client_id, client_data)

        if not client:
            return ClientResponse(
                error=f'Cliente com ID {client_id} não encontrado'
            )

        return ClientResponse(data=client_to_dict(client))
    except Exception as e:
        return ClientResponse(error=str(e))


@router.put(
    '/{client_id}/deactivate',
    response_model=ClientResponse,
    status_code=status.HTTP_200_OK,
)
async def deactivate_client(
    client_id: int = Path(..., description='ID do cliente'),
    db: Session = Depends(get_db),
):
    """
    Desativa um cliente (muda is_active para False)
    
    Não remove o cliente do banco de dados, apenas o marca como inativo.
    """
    try:
        success = ClientService.deactivate_client(db, client_id)

        if not success:
            return ClientResponse(
                error=f'Cliente com ID {client_id} não encontrado'
            )

        return ClientResponse(
            data=f'Cliente com ID {client_id} desativado com sucesso'
        )
    except Exception as e:
        return ClientResponse(error=str(e))
