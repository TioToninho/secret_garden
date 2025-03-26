from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MonthlyVariableValuesBase(BaseModel):
    """Modelo base para valores variáveis mensais"""
    month: int = Field(..., ge=1, le=12, description="Mês (1-12)")
    year: int = Field(..., ge=2000, le=2100, description="Ano")
    
    # Valores que podem variar mensalmente
    water_bill: Optional[float] = Field(None, description="Conta de água")
    gas_bill: Optional[float] = Field(None, description="Conta de gás")
    insurance: Optional[float] = Field(None, description="Seguro")
    property_tax: Optional[float] = Field(None, description="IPTU")
    condo_fee: Optional[float] = Field(None, description="Condomínio")
    condo_paid_by_agency: bool = Field(
        default=False, 
        description="Indica se o condomínio é pago pela imobiliária"
    )


class MonthlyVariableValuesCreate(MonthlyVariableValuesBase):
    """Modelo para criação de valores variáveis mensais"""
    client_id: int = Field(..., description="ID do cliente")


class MonthlyVariableValuesUpdate(MonthlyVariableValuesBase):
    """Modelo para atualização de valores variáveis mensais"""
    pass


class MonthlyVariableValuesResponse(BaseModel):
    """Modelo de resposta para valores variáveis mensais"""
    data: Optional[list[dict]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True 