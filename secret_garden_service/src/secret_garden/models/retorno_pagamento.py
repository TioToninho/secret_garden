from pydantic import BaseModel
from typing import Optional, List, Union, Dict, Any
from datetime import datetime, date


class RetornoPagamentoBase(BaseModel):
    """Modelo base para retorno de pagamentos"""
    client_id: int
    month: int
    year: int
    
    # Informações do boleto/pagamento
    due_date: date                 # Data de vencimento
    payment_date: date             # Data de pagamento
    rent_amount: float             # Valor do aluguel (título)
    amount_paid: float             # Valor efetivamente pago
    
    # Valores financeiros
    interest: float = 0.0          # Juros
    condo_fee: float = 0.0         # Condomínio
    percentage: float = 0.0        # Percentual
    commission: float = 0.0        # Comissão
    delivery_fee: float = 0.0      # Taxa de envio
    condo_paid: bool = False       # Pago condomínio
    owner_payment_amount: float = 0.0  # Valor a pagar ao proprietário


class RetornoPagamentoCreate(RetornoPagamentoBase):
    """Modelo para criação de retorno de pagamento"""
    pass


class RetornoPagamentoUpdate(BaseModel):
    """Modelo para atualização de retorno de pagamento"""
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    rent_amount: Optional[float] = None
    amount_paid: Optional[float] = None
    interest: Optional[float] = None
    condo_fee: Optional[float] = None
    percentage: Optional[float] = None
    commission: Optional[float] = None
    delivery_fee: Optional[float] = None
    condo_paid: Optional[bool] = None
    owner_payment_amount: Optional[float] = None


class RetornoPagamento(RetornoPagamentoBase):
    """Modelo completo de retorno de pagamento"""
    id: int
    processed_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class RetornoPagamentoResponse(BaseModel):
    """Modelo de resposta para operações com retornos de pagamento"""
    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None
    error: Optional[str] = None


class ProcessamentoRetornoRequest(BaseModel):
    """Modelo para solicitação de processamento de retorno"""
    client_name_prefix: str            # Prefixo do nome do cliente para busca
    payment_date: date                 # Data de pagamento
    amount_paid: float                 # Valor pago
    interest: float = 0.0              # Juros 