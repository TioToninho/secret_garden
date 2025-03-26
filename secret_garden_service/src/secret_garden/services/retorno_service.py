from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.secret_garden.database.models import Client, RetornoPagamento, MonthlyCalculation
from src.secret_garden.models.retorno_pagamento import RetornoPagamentoCreate


class RetornoService:
    """Serviço para processamento de retorno de pagamentos"""

    @staticmethod
    def buscar_clientes_por_nome(
        db: Session, nome_prefixo: str
    ) -> List[Dict[str, Any]]:
        """
        Busca clientes cujo nome começa com o prefixo informado
        
        Args:
            db: Sessão do banco de dados
            nome_prefixo: Prefixo do nome do cliente
            
        Returns:
            Lista de clientes que correspondem ao prefixo fornecido
        """
        clientes = db.query(Client).filter(
            Client.name.like(f"{nome_prefixo}%"),
            Client.is_active == True
        ).all()
        
        result = []
        for cliente in clientes:
            result.append({
                "id": cliente.id,
                "name": cliente.name,
                "owner_id": cliente.owner_id,
                "due_date": cliente.due_date,
                "condo_fee": cliente.condo_fee,
                "percentage": cliente.percentage,
                "delivery_fee": cliente.delivery_fee,
                "condo_paid": cliente.condo_paid
            })
            
        return result

    @staticmethod
    def processar_retorno(
        db: Session, 
        client_id: int, 
        payment_date: date,
        amount_paid: float,
        interest: float = 0.0
    ) -> Dict[str, Any]:
        """
        Processa o retorno de pagamento para um cliente
        
        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente
            payment_date: Data do pagamento
            amount_paid: Valor pago
            interest: Juros (opcional)
            
        Returns:
            Informações sobre o retorno processado
        """
        # Buscar o cliente
        cliente = db.query(Client).filter(Client.id == client_id).first()
        if not cliente:
            return {
                "success": False,
                "message": f"Cliente com ID {client_id} não encontrado"
            }
            
        # Obter o mês e ano do pagamento
        month = payment_date.month
        year = payment_date.year
        
        # Verificar se já existe um retorno para este cliente/mês/ano
        retorno_existente = db.query(RetornoPagamento).filter(
            and_(
                RetornoPagamento.client_id == client_id,
                RetornoPagamento.month == month,
                RetornoPagamento.year == year
            )
        ).first()
        
        if retorno_existente:
            return {
                "success": False,
                "message": f"Já existe um retorno processado para este cliente no mês {month}/{year}"
            }
            
        # Buscar o cálculo mensal correspondente para obter valores previstos
        calc_mensal = db.query(MonthlyCalculation).filter(
            and_(
                MonthlyCalculation.client_id == client_id,
                MonthlyCalculation.month == month,
                MonthlyCalculation.year == year
            )
        ).first()
        
        # Calcular a data de vencimento
        if cliente.due_date:
            try:
                vencimento_dia = cliente.due_date
                vencimento_data = date(year, month, vencimento_dia)
            except ValueError:
                # Lidar com dias inválidos (ex: 31 de fevereiro)
                # Usar o último dia do mês
                next_month = datetime(year, month, 1) + relativedelta(months=1)
                last_day = (next_month - relativedelta(days=1)).day
                vencimento_data = date(year, month, min(vencimento_dia, last_day))
        else:
            # Se não tiver vencimento definido, usar o 10º dia do mês
            vencimento_data = date(year, month, 10)
        
        # Calcular valores financeiros
        condo_fee = cliente.condo_fee or 0.0
        percentage = cliente.percentage or 0.0
        delivery_fee = cliente.delivery_fee or 0.0
        condo_paid = cliente.condo_paid or False
        
        # Se tiver cálculo mensal, usar os valores já calculados
        if calc_mensal:
            rent_amount = calc_mensal.rent_amount
            commission = calc_mensal.commission
        else:
            # Caso contrário, calcular valores básicos
            rent_amount = amount_paid  # Valor do título é igual ao valor pago por padrão
            commission = (amount_paid * percentage / 100.0)
        
        # Calcular valor a pagar ao proprietário
        owner_payment_amount = (amount_paid + interest - 
                              commission - delivery_fee - 
                              (1 if condo_paid else 0))
        
        # Criar o registro de retorno
        novo_retorno = RetornoPagamento(
            client_id=client_id,
            month=month,
            year=year,
            due_date=vencimento_data,
            payment_date=payment_date,
            rent_amount=rent_amount,
            amount_paid=amount_paid,
            interest=interest,
            condo_fee=condo_fee,
            percentage=percentage,
            commission=commission,
            delivery_fee=delivery_fee,
            condo_paid=condo_paid,
            owner_payment_amount=owner_payment_amount,
            processed_at=datetime.now()
        )
        
        db.add(novo_retorno)
        db.commit()
        db.refresh(novo_retorno)
        
        return {
            "success": True,
            "message": "Retorno processado com sucesso",
            "retorno_id": novo_retorno.id,
            "owner_payment_amount": owner_payment_amount
        }
    
    @staticmethod
    def get_retorno(db: Session, retorno_id: int) -> Optional[RetornoPagamento]:
        """Busca um retorno pelo ID"""
        return db.query(RetornoPagamento).filter(
            RetornoPagamento.id == retorno_id
        ).first()
    
    @staticmethod
    def get_retornos(
        db: Session, 
        client_id: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[RetornoPagamento]:
        """Busca retornos com filtros opcionais"""
        query = db.query(RetornoPagamento)
        
        if client_id:
            query = query.filter(RetornoPagamento.client_id == client_id)
        if month:
            query = query.filter(RetornoPagamento.month == month)
        if year:
            query = query.filter(RetornoPagamento.year == year)
            
        # Ordenar por data de processamento (mais recente primeiro)
        query = query.order_by(RetornoPagamento.processed_at.desc())
            
        return query.all()
    
    @staticmethod
    def get_retornos_by_owner(
        db: Session,
        owner_id: int,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[RetornoPagamento]:
        """Busca retornos para todos os clientes de um proprietário"""
        # Primeiro encontrar os IDs dos clientes deste proprietário
        client_ids = [c.id for c in db.query(Client.id).filter(
            Client.owner_id == owner_id, 
            Client.is_active == True
        ).all()]
        
        if not client_ids:
            return []
        
        # Depois buscar os retornos para estes clientes
        query = db.query(RetornoPagamento).filter(
            RetornoPagamento.client_id.in_(client_ids)
        )
        
        if month:
            query = query.filter(RetornoPagamento.month == month)
        if year:
            query = query.filter(RetornoPagamento.year == year)
            
        # Ordenar por data de processamento (mais recente primeiro)
        query = query.order_by(RetornoPagamento.processed_at.desc())
            
        return query.all()
        
    @staticmethod
    def retorno_to_dict(retorno: RetornoPagamento) -> Dict[str, Any]:
        """Converte um objeto RetornoPagamento para dicionário"""
        return {
            "id": retorno.id,
            "client_id": retorno.client_id,
            "month": retorno.month,
            "year": retorno.year,
            "due_date": retorno.due_date.isoformat() if retorno.due_date else None,
            "payment_date": retorno.payment_date.isoformat() if retorno.payment_date else None,
            "rent_amount": retorno.rent_amount,
            "amount_paid": retorno.amount_paid,
            "interest": retorno.interest,
            "condo_fee": retorno.condo_fee,
            "percentage": retorno.percentage,
            "commission": retorno.commission,
            "delivery_fee": retorno.delivery_fee,
            "condo_paid": retorno.condo_paid,
            "owner_payment_amount": retorno.owner_payment_amount,
            "processed_at": retorno.processed_at.isoformat() if retorno.processed_at else None,
            "updated_at": retorno.updated_at.isoformat() if retorno.updated_at else None
        } 