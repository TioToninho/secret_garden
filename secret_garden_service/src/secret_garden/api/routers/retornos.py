from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from src.secret_garden.database.config import get_db
from src.secret_garden.models.retorno_pagamento import (
    RetornoPagamentoResponse, ProcessamentoRetornoRequest
)
from src.secret_garden.services.retorno_service import RetornoService

router = APIRouter(
    prefix="/api/retornos",
    tags=["retornos"],
    responses={404: {"description": "Not found"}},
)


@router.post("/buscar-clientes", response_model=RetornoPagamentoResponse)
async def buscar_clientes_por_nome(
    nome_prefixo: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Busca clientes cujo nome começa com o prefixo informado.
    
    Utilizado para sugerir clientes ao processar um retorno.
    """
    try:
        clientes = RetornoService.buscar_clientes_por_nome(db, nome_prefixo)
        return {"data": clientes, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.post("/processar", response_model=RetornoPagamentoResponse)
async def processar_retorno(
    retorno_request: ProcessamentoRetornoRequest = Body(...),
    client_id: int = Body(...),
    db: Session = Depends(get_db)
):
    """
    Processa um retorno de pagamento para um cliente específico.
    
    Recebe os dados básicos do retorno e o ID do cliente selecionado.
    """
    try:
        result = RetornoService.processar_retorno(
            db=db,
            client_id=client_id,
            payment_date=retorno_request.payment_date,
            amount_paid=retorno_request.amount_paid,
            interest=retorno_request.interest
        )
        
        if not result["success"]:
            return {"data": None, "error": result["message"]}
            
        return {"data": result, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.get("/", response_model=RetornoPagamentoResponse)
async def listar_retornos(
    client_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Ano"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os retornos de pagamento com filtros opcionais.
    """
    try:
        retornos = RetornoService.get_retornos(
            db, client_id=client_id, month=month, year=year
        )
        
        if not retornos:
            return {"data": [], "error": None}
            
        # Converter objetos SQLAlchemy em dicionários
        retornos_dict = [RetornoService.retorno_to_dict(r) for r in retornos]
        
        return {"data": retornos_dict, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.get("/owner/{owner_id}", response_model=RetornoPagamentoResponse)
async def listar_retornos_por_proprietario(
    owner_id: int = Path(..., description="ID do proprietário"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Ano"),
    db: Session = Depends(get_db)
):
    """
    Lista retornos de pagamento de todos os clientes de um proprietário.
    """
    try:
        retornos = RetornoService.get_retornos_by_owner(
            db, owner_id=owner_id, month=month, year=year
        )
        
        if not retornos:
            return {"data": [], "error": None}
            
        # Converter objetos SQLAlchemy em dicionários
        retornos_dict = [RetornoService.retorno_to_dict(r) for r in retornos]
        
        return {"data": retornos_dict, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


@router.get("/{retorno_id}", response_model=RetornoPagamentoResponse)
async def obter_retorno(
    retorno_id: int = Path(..., description="ID do retorno"),
    db: Session = Depends(get_db)
):
    """
    Obtém os detalhes de um retorno de pagamento específico pelo ID.
    """
    try:
        retorno = RetornoService.get_retorno(db, retorno_id)
        
        if not retorno:
            return {
                "data": None, 
                "error": f"Retorno com ID {retorno_id} não encontrado"
            }
            
        # Converter objeto SQLAlchemy em dicionário
        retorno_dict = RetornoService.retorno_to_dict(retorno)
        
        return {"data": retorno_dict, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)} 