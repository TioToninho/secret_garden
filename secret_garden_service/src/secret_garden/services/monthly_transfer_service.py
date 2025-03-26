from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.secret_garden.database.models import (
    Client, MonthlyCalculation, MonthlyVariableValues
)


class MonthlyTransferService:
    """Serviço para gerenciar repasses mensais"""

    @staticmethod
    def get_owner_transfers(
        db: Session,
        owner_id: int,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retorna os dados de repasse mensal para um proprietário específico.

        Args:
            db: Sessão do banco de dados
            owner_id: ID do proprietário
            month: Mês para filtrar (opcional)
            year: Ano para filtrar (opcional)

        Returns:
            Dicionário com os dados do repasse, resumo e metadados
        """
        # Se mês e ano não forem fornecidos, usar o mês e ano atuais
        if not month or not year:
            now = datetime.now()
            month = month or now.month
            year = year or now.year

        # Buscar todos os clientes ativos do proprietário
        clients = (
            db.query(Client)
            .filter(
                Client.owner_id == owner_id,
                Client.is_active.is_(True)
            )
            .all()
        )

        if not clients:
            return {
                "data": [],
                "summary": {
                    "total_rent": 0,
                    "total_commission": 0,
                    "total_condo_fees": 0,
                    "total_delivery_fees": 0,
                    "total_deposit": 0,
                    "total_properties": 0
                },
                "metadata": {
                    "owner_id": owner_id,
                    "month": month,
                    "year": year,
                    "generated_at": datetime.now()
                }
            }

        # Lista para armazenar os dados de repasse
        transfer_items = []
        
        # Variáveis para o resumo
        summary = {
            "total_rent": 0,
            "total_commission": 0,
            "total_condo_fees": 0,
            "total_delivery_fees": 0,
            "total_deposit": 0,
            "total_properties": len(clients)
        }

        # Para cada cliente, buscar os cálculos e valores variáveis do mês
        for client in clients:
            # Buscar cálculo mensal
            calculation = (
                db.query(MonthlyCalculation)
                .filter(
                    and_(
                        MonthlyCalculation.client_id == client.id,
                        MonthlyCalculation.month == month,
                        MonthlyCalculation.year == year
                    )
                )
                .first()
            )

            # Buscar valores variáveis se o cliente tiver variação mensal
            variable_values = None
            if client.has_monthly_variation:
                variable_values = (
                    db.query(MonthlyVariableValues)
                    .filter(
                        and_(
                            MonthlyVariableValues.client_id == client.id,
                            MonthlyVariableValues.month == month,
                            MonthlyVariableValues.year == year
                        )
                    )
                    .first()
                )

            # Se encontrou cálculo, criar item de repasse
            if calculation:
                # Determinar valor do condomínio (fixo ou variável)
                condo_fee = (
                    variable_values.condo_fee
                    if variable_values and variable_values.condo_fee is not None
                    else client.condo_fee
                )

                # Determinar se condomínio é pago pela imobiliária
                condo_paid = (
                    variable_values.condo_paid_by_agency
                    if variable_values and variable_values.condo_paid_by_agency is not None
                    else client.condo_paid
                )

                # Garantir que condo_paid seja sempre um booleano
                condo_paid = bool(condo_paid) if condo_paid is not None else False

                transfer_item = {
                    "id": calculation.id,
                    "tenant": {
                        "id": client.id,
                        "name": client.name
                    },
                    "month": month,
                    "year": year,
                    "due_date": client.due_date,
                    "rent_amount": calculation.rent_amount,
                    "amount_paid": client.amount_paid,
                    "payment_date": client.payment_date,
                    "condo_fee": condo_fee,
                    "condo_paid_by_agency": condo_paid,
                    "calculation_base": calculation.calculation_base,
                    "percentage": client.percentage,
                    "commission": calculation.commission,
                    "delivery_fee": client.delivery_fee,
                    "deposit_amount": calculation.deposit_amount,
                    "created_at": calculation.created_at,
                    "updated_at": calculation.updated_at
                }

                transfer_items.append(transfer_item)

                # Atualizar resumo
                summary["total_rent"] += calculation.rent_amount
                summary["total_commission"] += calculation.commission
                summary["total_condo_fees"] += (condo_fee or 0)
                summary["total_delivery_fees"] += (client.delivery_fee or 0)
                summary["total_deposit"] += calculation.deposit_amount

        return {
            "data": transfer_items,
            "summary": summary,
            "metadata": {
                "owner_id": owner_id,
                "month": month,
                "year": year,
                "generated_at": datetime.now()
            }
        } 