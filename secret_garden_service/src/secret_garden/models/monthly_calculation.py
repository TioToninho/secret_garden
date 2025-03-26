from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MonthlyCalculationBase(BaseModel):
    """Modelo base para cálculos mensais"""

    client_id: int
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    rent_amount: float
    calculation_base: float
    tenant_payment: float
    commission: float
    deposit_amount: float


class MonthlyCalculationCreate(MonthlyCalculationBase):
    """Modelo para criação de cálculos mensais"""

    pass


class MonthlyCalculationUpdate(MonthlyCalculationBase):
    """Modelo para atualização de cálculos mensais"""

    pass


class MonthlyCalculation(MonthlyCalculationBase):
    """Modelo completo de cálculo mensal"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class MonthlyCalculationResponse(BaseModel):
    """Modelo de resposta para operações com cálculos mensais"""

    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class MonthlyCalculationSummary(BaseModel):
    """Resumo dos cálculos mensais"""

    total_processed: int
    successful: int
    failed: int
    message: str


class TenantInfo(BaseModel):
    """Informações do locatário para o repasse"""
    id: int
    name: str


class MonthlyTransferItem(BaseModel):
    """Item individual do repasse mensal"""
    id: int
    tenant: TenantInfo
    month: int
    year: int
    due_date: Optional[datetime]
    rent_amount: float
    amount_paid: Optional[float]
    payment_date: Optional[datetime]
    condo_fee: Optional[float]
    condo_paid_by_agency: bool = False
    calculation_base: float
    percentage: Optional[float]
    commission: float
    delivery_fee: Optional[float]
    deposit_amount: float
    created_at: datetime
    updated_at: Optional[datetime]


class MonthlyTransferSummary(BaseModel):
    """Resumo dos valores do repasse mensal"""
    total_rent: float = 0
    total_commission: float = 0
    total_condo_fees: float = 0
    total_delivery_fees: float = 0
    total_deposit: float = 0
    total_properties: int = 0


class MonthlyTransferMetadata(BaseModel):
    """Metadados do repasse mensal"""
    owner_id: int
    month: int
    year: int
    generated_at: datetime = Field(default_factory=datetime.now)


class MonthlyTransferResponse(BaseModel):
    """Resposta completa do repasse mensal"""
    data: List[MonthlyTransferItem]
    summary: MonthlyTransferSummary
    metadata: MonthlyTransferMetadata

    class Config:
        from_attributes = True
