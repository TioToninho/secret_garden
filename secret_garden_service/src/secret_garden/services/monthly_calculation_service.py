import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.secret_garden.database.models import Client, MonthlyCalculation, MonthlyVariableValues

logger = logging.getLogger(__name__)


class MonthlyCalculationService:
    """Serviço para cálculo financeiro mensal de clientes"""

    @staticmethod
    async def calculate_for_all_clients(
        db: Session, month: Optional[int] = None, year: Optional[int] = None
    ) -> Dict:
        """
        Calcula os valores financeiros mensais para todos os clientes ativos.

        Args:
            db: Sessão do banco de dados
            month: Mês para calcular (1-12). Se não for fornecido, usa o mês atual
            year: Ano para calcular. Se não for fornecido, usa o ano atual

        Returns:
            Dict com informações sobre o processamento
        """
        # Se mês e ano não forem fornecidos, usar o mês e ano atuais
        if not month or not year:
            now = datetime.now()
            month = month or now.month
            year = year or now.year

        # Buscar todos os clientes ativos
        clients = db.query(Client).filter(Client.is_active.is_(True)).all()

        if not clients:
            return {
                'total_processed': 0,
                'successful': 0,
                'failed': 0,
                'message': 'Nenhum cliente ativo encontrado.',
            }

        # Cálculo assíncrono para todos os clientes
        tasks = []
        for client in clients:
            task = asyncio.create_task(
                MonthlyCalculationService._calculate_for_client(
                    db, client, month, year
                )
            )
            tasks.append(task)

        # Aguardar todas as tarefas concluírem
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Contar sucessos e falhas
        successful = sum(1 for r in results if r is True)
        failed = sum(
            1 for r in results if r is False or isinstance(r, Exception)
        )

        return {
            'total_processed': len(clients),
            'successful': successful,
            'failed': failed,
            'message': f'Processamento concluído. {successful} sucessos, {failed} falhas.',
        }

    @staticmethod
    async def _calculate_for_client(
        db: Session, client: Client, month: int, year: int
    ) -> bool:
        """
        Calcula os valores financeiros mensais para um cliente específico.

        Args:
            db: Sessão do banco de dados
            client: Instância do cliente
            month: Mês para calcular (1-12)
            year: Ano para calcular

        Returns:
            True se o cálculo foi bem-sucedido, False caso contrário
        """
        try:
            # Verificar se já existe um cálculo para este cliente/mês/ano
            existing = (
                db.query(MonthlyCalculation)
                .filter(
                    and_(
                        MonthlyCalculation.client_id == client.id,
                        MonthlyCalculation.month == month,
                        MonthlyCalculation.year == year,
                    )
                )
                .first()
            )

            # Definir valores padrão (valores fixos do cliente)
            property_tax = client.property_tax or 0
            utilities = client.utilities or 0
            condo_fee = client.condo_fee or 0
            insurance = client.insurance or 0
            condo_paid = client.condo_paid

            # Se o cliente tem variação mensal, buscar valores variáveis
            if client.has_monthly_variation:
                # Buscar registro na tabela de valores variáveis mensais
                variable_values = (
                    db.query(MonthlyVariableValues)
                    .filter(
                        and_(
                            MonthlyVariableValues.client_id == client.id,
                            MonthlyVariableValues.month == month,
                            MonthlyVariableValues.year == year,
                        )
                    )
                    .first()
                )

                # Se encontrou valores variáveis, usar estes valores em vez dos valores fixos
                if variable_values:
                    logger.info(
                        f"Usando valores variáveis para cliente {client.id} no mês {month}/{year}"
                    )
                    # Substituir apenas valores que estão preenchidos na tabela de valores variáveis
                    if variable_values.property_tax is not None:
                        property_tax = variable_values.property_tax
                    if variable_values.water_bill is not None or variable_values.gas_bill is not None:
                        # Água/Gás é a soma das contas de água e gás
                        utilities = (variable_values.water_bill or 0) + (variable_values.gas_bill or 0)
                    if variable_values.condo_fee is not None:
                        condo_fee = variable_values.condo_fee
                    if variable_values.insurance is not None:
                        insurance = variable_values.insurance
                    if variable_values.condo_paid_by_agency is not None:
                        condo_paid = variable_values.condo_paid_by_agency

            # Calcular os valores
            # Valor do aluguel = Valor pago + IPTU + Água/Gás
            rent_amount = round(
                (client.amount_paid or 0)
                + property_tax
                + utilities,
                2,
            )

            # Base de cálculo = IPTU + Água/Gás + Condomínio + Seguro
            calculation_base = round(
                property_tax
                + utilities
                + condo_fee
                + insurance,
                2,
            )

            # Valor pago pelo locatário = Valor aluguel - Base cálculo
            tenant_payment = round(rent_amount - calculation_base, 2)

            # Comissão = Valor pago pelo locatário * (Percentual / 100)
            commission = round(
                tenant_payment * ((client.percentage or 0) / 100), 2
            )

            # Valor depósito = Valor aluguel - Comissão - Taxa envio - Condo pago
            deposit_amount = round(
                rent_amount
                - commission
                - (client.delivery_fee or 0)
                - (condo_fee if condo_paid else 0),
                2,
            )

            # Se já existe, atualizar
            if existing:
                existing.rent_amount = rent_amount
                existing.calculation_base = calculation_base
                existing.tenant_payment = tenant_payment
                existing.commission = commission
                existing.deposit_amount = deposit_amount
                existing.updated_at = datetime.now()
            else:
                # Se não existe, criar novo
                new_calculation = MonthlyCalculation(
                    client_id=client.id,
                    month=month,
                    year=year,
                    rent_amount=rent_amount,
                    calculation_base=calculation_base,
                    tenant_payment=tenant_payment,
                    commission=commission,
                    deposit_amount=deposit_amount,
                )
                db.add(new_calculation)

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            logger.error(
                f'Erro ao calcular para cliente {client.id}: {str(e)}'
            )
            return False
