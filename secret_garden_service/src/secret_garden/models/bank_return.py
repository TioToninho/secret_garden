from datetime import date, datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class BankReturnBase(BaseModel):
    """Modelo base para retornos bancários"""
    client_id: int
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    payer_name: Optional[str] = None
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    title_amount: Optional[float] = None
    charged_amount: Optional[float] = None
    variation_amount: Optional[float] = None


class BankReturnCreate(BankReturnBase):
    """Modelo para criação de retornos bancários"""
    pass


class BankReturnUpdate(BaseModel):
    """Modelo para atualização de retornos bancários"""
    payer_name: Optional[str] = None
    due_date: Optional[date] = None
    payment_date: Optional[date] = None
    title_amount: Optional[float] = None
    charged_amount: Optional[float] = None
    variation_amount: Optional[float] = None


class BankReturnInDB(BankReturnBase):
    """Modelo para retornos bancários no banco de dados"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BankReturnSummary(BaseModel):
    """Resumo dos valores de retorno bancário"""
    total_title_amount: float = 0
    total_charged_amount: float = 0
    total_variation_amount: float = 0
    total_returns: int = 0


class BankReturnMetadata(BaseModel):
    """Metadados do retorno bancário"""
    owner_id: Optional[int] = None
    month: int
    year: int
    generated_at: datetime = Field(default_factory=datetime.now)


class BankReturnResponse(BaseModel):
    """Resposta para operações com retornos bancários"""
    data: Optional[List[Dict[str, Any]]] = None
    summary: Optional[BankReturnSummary] = None
    metadata: Optional[BankReturnMetadata] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True 