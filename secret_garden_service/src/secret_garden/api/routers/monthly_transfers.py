from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from src.secret_garden.database.config import get_db
from src.secret_garden.models.monthly_calculation import MonthlyTransferResponse
from src.secret_garden.services.monthly_transfer_service import MonthlyTransferService

router = APIRouter(
    prefix='/api/monthly-transfers',
    tags=['monthly-transfers'],
    responses={404: {'description': 'Not found'}},
)


@router.get('/owner/{owner_id}', response_model=MonthlyTransferResponse)
async def get_owner_transfers(
    owner_id: int = Path(..., title="ID do proprietário", gt=0),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Ano"),
    db: Session = Depends(get_db),
):
    """
    Retorna os dados de repasse mensal para um proprietário específico.
    
    Inclui:
    - Lista de imóveis com valores calculados
    - Resumo dos totais
    - Metadados do repasse
    
    Se mês e ano não forem fornecidos, usa o mês e ano atuais.
    """
    result = MonthlyTransferService.get_owner_transfers(
        db, owner_id, month, year
    )
    return result 