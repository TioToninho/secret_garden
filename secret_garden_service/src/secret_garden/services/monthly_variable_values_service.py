from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.secret_garden.database.models import (
    Client, MonthlyVariableValues
)
from src.secret_garden.models.monthly_variable_values import (
    MonthlyVariableValuesCreate, MonthlyVariableValuesUpdate
)


class MonthlyVariableValuesService:
    """Serviço para gerenciar valores variáveis mensais"""

    @staticmethod
    def get_monthly_values(
        db: Session,
        client_id: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[MonthlyVariableValues]:
        """
        Busca valores variáveis mensais com filtros opcionais.
        
        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente para filtrar
            month: Mês para filtrar (1-12)
            year: Ano para filtrar
            
        Returns:
            Lista de valores variáveis mensais
        """
        query = db.query(MonthlyVariableValues)

        if client_id:
            query = query.filter(MonthlyVariableValues.client_id == client_id)
        if month:
            query = query.filter(MonthlyVariableValues.month == month)
        if year:
            query = query.filter(MonthlyVariableValues.year == year)

        return query.all()

    @staticmethod
    def get_monthly_value(
        db: Session,
        client_id: int,
        month: int,
        year: int
    ) -> Optional[MonthlyVariableValues]:
        """
        Busca valores variáveis mensais de um cliente específico.
        
        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente
            month: Mês (1-12)
            year: Ano
            
        Returns:
            Valores variáveis mensais do cliente ou None se não encontrado
        """
        return db.query(MonthlyVariableValues).filter(
            MonthlyVariableValues.client_id == client_id,
            MonthlyVariableValues.month == month,
            MonthlyVariableValues.year == year
        ).first()

    @staticmethod
    def create_or_update_monthly_values(
        db: Session,
        monthly_values: MonthlyVariableValuesCreate
    ) -> MonthlyVariableValues:
        """
        Cria ou atualiza valores variáveis mensais para um cliente.
        
        Se já existir um registro para o mesmo cliente/mês/ano, atualiza.
        Caso contrário, cria um novo registro.
        
        Args:
            db: Sessão do banco de dados
            monthly_values: Dados dos valores variáveis mensais
            
        Returns:
            Valores variáveis mensais criados/atualizados
        """
        # Verificar se já existe um registro para este cliente/mês/ano
        existing_values = MonthlyVariableValuesService.get_monthly_value(
            db,
            monthly_values.client_id,
            monthly_values.month,
            monthly_values.year
        )

        if existing_values:
            # Se existir, atualizar os valores
            for field, value in monthly_values.dict(exclude={'client_id'}).items():
                setattr(existing_values, field, value)
            db.commit()
            db.refresh(existing_values)
            return existing_values

        # Se não existir, criar novo registro
        db_monthly_values = MonthlyVariableValues(
            client_id=monthly_values.client_id,
            month=monthly_values.month,
            year=monthly_values.year,
            water_bill=monthly_values.water_bill,
            gas_bill=monthly_values.gas_bill,
            insurance=monthly_values.insurance,
            property_tax=monthly_values.property_tax,
            condo_fee=monthly_values.condo_fee,
            condo_paid_by_agency=monthly_values.condo_paid_by_agency
        )
        db.add(db_monthly_values)
        db.commit()
        db.refresh(db_monthly_values)
        return db_monthly_values

    @staticmethod
    def update_monthly_values(
        db: Session,
        client_id: int,
        month: int,
        year: int,
        monthly_values: MonthlyVariableValuesUpdate
    ) -> Optional[MonthlyVariableValues]:
        """
        Atualiza valores variáveis mensais de um cliente.
        
        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente
            month: Mês (1-12)
            year: Ano
            monthly_values: Novos valores variáveis mensais
            
        Returns:
            Valores variáveis mensais atualizados ou None se não encontrado
        """
        db_monthly_values = MonthlyVariableValuesService.get_monthly_value(
            db, client_id, month, year
        )
        
        if not db_monthly_values:
            return None
            
        # Atualizar apenas os campos fornecidos
        for field, value in monthly_values.dict(exclude_unset=True).items():
            setattr(db_monthly_values, field, value)
            
        db.commit()
        db.refresh(db_monthly_values)
        return db_monthly_values

    @staticmethod
    def delete_monthly_values(
        db: Session,
        client_id: int,
        month: int,
        year: int
    ) -> bool:
        """
        Remove valores variáveis mensais de um cliente.
        
        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente
            month: Mês (1-12)
            year: Ano
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        db_monthly_values = MonthlyVariableValuesService.get_monthly_value(
            db, client_id, month, year
        )
        
        if not db_monthly_values:
            return False
            
        db.delete(db_monthly_values)
        db.commit()
        return True

    @staticmethod
    def monthly_values_to_dict(
        monthly_values: MonthlyVariableValues
    ) -> Dict[str, Any]:
        """
        Converte um objeto MonthlyVariableValues em um dicionário.
        
        Args:
            monthly_values: Objeto MonthlyVariableValues
            
        Returns:
            Dicionário com os valores variáveis mensais
        """
        return {
            'id': monthly_values.id,
            'client_id': monthly_values.client_id,
            'month': monthly_values.month,
            'year': monthly_values.year,
            'water_bill': monthly_values.water_bill,
            'gas_bill': monthly_values.gas_bill,
            'insurance': monthly_values.insurance,
            'property_tax': monthly_values.property_tax,
            'condo_fee': monthly_values.condo_fee,
            'condo_paid_by_agency': monthly_values.condo_paid_by_agency,
            'created_at': monthly_values.created_at or datetime.now(),
            'updated_at': monthly_values.updated_at
        }
        
    @staticmethod
    def check_and_create_pending_values(
        db: Session, 
        current_month: Optional[int] = None,
        current_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Verifica e cria valores pendentes para clientes com variação mensal.
        
        Esta função busca todos os clientes ativos que têm variação mensal
        (has_monthly_variation=True) e cria registros vazios para o mês atual
        se ainda não existirem.
        
        Args:
            db: Sessão do banco de dados
            current_month: Mês atual (opcional, padrão usa o mês atual)
            current_year: Ano atual (opcional, padrão usa o ano atual)
            
        Returns:
            Lista de clientes com valores pendentes, incluindo nome e ID
        """
        # Usar o mês e ano atual se não fornecidos
        if current_month is None or current_year is None:
            today = datetime.now()
            current_month = current_month or today.month
            current_year = current_year or today.year
            
        # Buscar todos os clientes ativos com variação mensal
        clients_with_variation = db.query(Client).filter(
            Client.is_active.is_(True),
            Client.has_monthly_variation.is_(True)
        ).all()
        
        # Lista de clientes com valores pendentes
        pending_clients = []
        
        for client in clients_with_variation:
            # Verificar se já existe registro para este mês/ano
            existing_values = MonthlyVariableValuesService.get_monthly_value(
                db, client.id, current_month, current_year
            )
            
            campos_verificados = [
                "water_bill", "gas_bill", "insurance", 
                "property_tax", "condo_fee"
            ]
            
            # Se não existir, criar um registro vazio
            if not existing_values:
                # Criar valores padrão vazios
                new_values = MonthlyVariableValuesCreate(
                    client_id=client.id,
                    month=current_month,
                    year=current_year,
                    water_bill=None,
                    gas_bill=None,
                    insurance=None,
                    property_tax=None,
                    condo_fee=None,
                    condo_paid_by_agency=False
                )
                
                # Criar o registro no banco
                MonthlyVariableValuesService.create_or_update_monthly_values(
                    db, new_values
                )
                
                # Adicionar à lista de pendentes
                client_info = {
                    "id": client.id,
                    "name": client.name,
                    "owner_id": client.owner_id,
                    "month": current_month,
                    "year": current_year,
                    "needs_filling": True,
                    "empty_fields": campos_verificados.copy()
                }
                pending_clients.append(client_info)
            else:
                # Verificar quais campos estão vazios
                campos_vazios = []
                for campo in campos_verificados:
                    if getattr(existing_values, campo) is None:
                        campos_vazios.append(campo)
                
                # Se houver campos vazios, adicionar à lista de pendentes
                if campos_vazios:
                    client_info = {
                        "id": client.id,
                        "name": client.name,
                        "owner_id": client.owner_id,
                        "month": current_month,
                        "year": current_year,
                        "needs_filling": True,
                        "empty_fields": campos_vazios
                    }
                    pending_clients.append(client_info)
                
        return pending_clients 