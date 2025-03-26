from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class ClientBase(BaseModel):
    """Modelo base para clientes"""

    name: str                             # Locatário (anteriormente tenant_name)
    owner_id: int                         # Locador (ID do proprietário)
    status: str                           # Situação
    due_date: Optional[int] = None        # Vencimento (dia do mês)

    # Valores financeiros
    amount_paid: Optional[float] = None   # Valor efetivamente pago
    property_tax: Optional[float] = None  # IPTU
    interest: Optional[float] = None      # Juros
    utilities: Optional[float] = None     # Água/Gás
    insurance: Optional[float] = None     # Seguro
    condo_fee: Optional[float] = None     # Condomínio
    percentage: Optional[float] = None    # %
    delivery_fee: Optional[float] = None  # Taxa de envio

    # Datas
    start_date: Optional[date] = None     # Início
    condo_paid: bool = False              # Pago condomínio
    withdrawal_date: Optional[date] = None  # Data ret
    withdrawal_number: Optional[str] = None  # nº ret
    payment_date: Optional[date] = None   # Data pagamento

    # Outros
    notes: Optional[str] = None           # Observações

    # Campos de controle
    has_monthly_variation: bool = False
    is_active: bool = True


class ClientCreate(ClientBase):
    """Modelo para criação de clientes"""

    pass


class ClientUpdate(BaseModel):
    """Modelo para atualização de clientes"""

    name: Optional[str] = None            # Anteriormente tenant_name
    owner_id: Optional[int] = None
    status: Optional[str] = None
    due_date: Optional[int] = None

    # Valores financeiros
    amount_paid: Optional[float] = None
    property_tax: Optional[float] = None
    interest: Optional[float] = None
    utilities: Optional[float] = None
    insurance: Optional[float] = None
    condo_fee: Optional[float] = None
    percentage: Optional[float] = None
    delivery_fee: Optional[float] = None

    # Datas
    start_date: Optional[date] = None
    condo_paid: Optional[bool] = None
    withdrawal_date: Optional[date] = None
    withdrawal_number: Optional[str] = None
    payment_date: Optional[date] = None

    # Outros
    notes: Optional[str] = None

    # Campos de controle
    has_monthly_variation: Optional[bool] = None
    is_active: Optional[bool] = None


class Client(ClientBase):
    """Modelo completo de cliente"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class ClientResponse(BaseModel):
    """Modelo de resposta padrão para operações com clientes"""

    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None
    error: Optional[str] = None


class AdjustmentInfo(BaseModel):
    """Informações sobre um reajuste de contrato"""
    id: int
    name: str
    start_date: str
    next_adjustment: str
    owner_id: int


class AdjustmentResponse(BaseModel):
    """Modelo de resposta para verificação de reajustes"""
    total: int
    contratos_reajuste: List[Dict[str, Any]]
    message: str
