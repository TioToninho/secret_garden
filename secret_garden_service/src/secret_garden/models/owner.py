from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class OwnerBase(BaseModel):
    """Modelo base para proprietários"""

    name: str


class OwnerCreate(OwnerBase):
    """Modelo para criação de proprietários"""

    pass


class OwnerUpdate(BaseModel):
    """Modelo para atualização de proprietários"""

    name: Optional[str] = None


class Owner(OwnerBase):
    """Modelo completo de proprietário"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


class OwnerResponse(BaseModel):
    """Modelo de resposta para operações com proprietários"""

    data: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None
    error: Optional[str] = None
