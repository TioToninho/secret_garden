from datetime import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.secret_garden.database.models import BankReturn, Client


class BankReturnService:
    """Serviço para gerenciar retornos bancários"""

    @staticmethod
    def create_or_update_bank_return(
        db: Session, client_id: int, month: int, year: int, data: Dict[str, Any]
    ) -> Optional[BankReturn]:
        """
        Cria ou atualiza um retorno bancário para um cliente.

        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente
            month: Mês do retorno
            year: Ano do retorno
            data: Dados do retorno bancário

        Returns:
            Instância do retorno bancário criado/atualizado
        """
        try:
            # Verificar se já existe um retorno para este cliente/mês/ano
            bank_return = (
                db.query(BankReturn)
                .filter(
                    and_(
                        BankReturn.client_id == client_id,
                        BankReturn.month == month,
                        BankReturn.year == year,
                    )
                )
                .first()
            )

            if bank_return:
                # Atualizar campos existentes
                for key, value in data.items():
                    setattr(bank_return, key, value)
                bank_return.updated_at = datetime.now()
            else:
                # Criar novo retorno
                bank_return = BankReturn(
                    client_id=client_id,
                    month=month,
                    year=year,
                    **data
                )
                db.add(bank_return)

            db.commit()
            db.refresh(bank_return)
            return bank_return

        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def get_owner_bank_returns(
        db: Session,
        owner_id: int,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retorna os dados de retorno bancário para um proprietário específico.

        Args:
            db: Sessão do banco de dados
            owner_id: ID do proprietário
            month: Mês para filtrar (opcional)
            year: Ano para filtrar (opcional)

        Returns:
            Dicionário com os dados dos retornos, resumo e metadados
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
                    "total_title_amount": 0,
                    "total_charged_amount": 0,
                    "total_variation_amount": 0,
                    "total_returns": 0
                },
                "metadata": {
                    "owner_id": owner_id,
                    "month": month,
                    "year": year,
                    "generated_at": datetime.now()
                }
            }

        # Lista para armazenar os dados de retorno
        return_items = []
        
        # Variáveis para o resumo
        summary = {
            "total_title_amount": 0,
            "total_charged_amount": 0,
            "total_variation_amount": 0,
            "total_returns": 0
        }

        # Para cada cliente, buscar os retornos bancários do mês
        for client in clients:
            bank_return = (
                db.query(BankReturn)
                .filter(
                    and_(
                        BankReturn.client_id == client.id,
                        BankReturn.month == month,
                        BankReturn.year == year
                    )
                )
                .first()
            )

            if bank_return:
                return_item = {
                    "id": bank_return.id,
                    "client": {
                        "id": client.id,
                        "name": client.name
                    },
                    "month": month,
                    "year": year,
                    "payer_name": bank_return.payer_name,
                    "due_date": bank_return.due_date,
                    "payment_date": bank_return.payment_date,
                    "title_amount": bank_return.title_amount,
                    "charged_amount": bank_return.charged_amount,
                    "variation_amount": bank_return.variation_amount,
                    "created_at": bank_return.created_at,
                    "updated_at": bank_return.updated_at
                }

                return_items.append(return_item)

                # Atualizar resumo
                summary["total_title_amount"] += (bank_return.title_amount or 0)
                summary["total_charged_amount"] += (bank_return.charged_amount or 0)
                summary["total_variation_amount"] += (bank_return.variation_amount or 0)
                summary["total_returns"] += 1

        return {
            "data": return_items,
            "summary": summary,
            "metadata": {
                "owner_id": owner_id,
                "month": month,
                "year": year,
                "generated_at": datetime.now()
            }
        } 