from datetime import datetime, date
from typing import Any, Dict, List, Optional
from dateutil.relativedelta import relativedelta

from sqlalchemy.orm import Session

from src.secret_garden.database.models import Client
from src.secret_garden.models.client import ClientCreate, ClientUpdate


class ClientService:
    @staticmethod
    def create_client(db: Session, client_data: ClientCreate) -> Client:
        """Cria um novo cliente"""
        # Convertemos o modelo Pydantic para um dicionário e criamos o modelo SQLAlchemy
        client_dict = client_data.dict()
        db_client = Client(**client_dict, created_at=datetime.now())

        db.add(db_client)
        db.commit()
        db.refresh(db_client)

        return db_client

    @staticmethod
    def get_client(db: Session, client_id: int) -> Optional[Client]:
        """Busca um cliente pelo ID"""
        return (
            db.query(Client)
            .filter(Client.id == client_id, Client.is_active)
            .first()
        )

    @staticmethod
    def get_clients(
        db: Session, filters: Dict[str, Any] = None
    ) -> List[Client]:
        """Busca todos os clientes com filtros opcionais"""
        if filters is None:
            filters = {}

        query = db.query(Client)

        # Aplicar filtros
        if 'is_active' in filters:
            query = query.filter(Client.is_active == filters['is_active'])

        if 'has_monthly_variation' in filters:
            has_variation = filters['has_monthly_variation']
            query = query.filter(Client.has_monthly_variation == has_variation)

        if 'owner_id' in filters:
            query = query.filter(Client.owner_id == filters['owner_id'])

        return query.all()

    @staticmethod
    def update_client(
        db: Session, client_id: int, client_data: ClientUpdate
    ) -> Optional[Client]:
        """Atualiza um cliente existente"""
        db_client = ClientService.get_client(db, client_id)

        if not db_client:
            return None

        update_data = client_data.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_client, key, value)

        db_client.updated_at = datetime.now()
        db.commit()
        db.refresh(db_client)

        return db_client

    @staticmethod
    def deactivate_client(db: Session, client_id: int) -> bool:
        """
        Desativa um cliente (muda is_active para False)
        
        Args:
            db: Sessão do banco de dados
            client_id: ID do cliente a ser desativado
            
        Returns:
            True se o cliente foi desativado com sucesso, False caso contrário
        """
        db_client = db.query(Client).filter(Client.id == client_id).first()
        if not db_client:
            return False
            
        db_client.is_active = False
        db_client.updated_at = datetime.now()
        db.commit()
        
        return True

    @staticmethod
    def calcular_proximo_reajuste(start_date: date) -> Optional[date]:
        """
        Calcula a próxima data de reajuste com base na data de início do contrato.
        O reajuste ocorre anualmente no aniversário do contrato.
        
        Args:
            start_date: Data de início do contrato
            
        Returns:
            A próxima data de reajuste
        """
        if not start_date:
            return None
            
        # Data atual
        hoje = datetime.now().date()
        
        # Calculamos o próximo aniversário do contrato
        proximo_aniversario = date(hoje.year, start_date.month, start_date.day)
        
        # Se o próximo aniversário já passou, adicionamos um ano
        if proximo_aniversario < hoje:
            proximo_aniversario = date(
                hoje.year + 1, 
                start_date.month, 
                start_date.day
            )
            
        return proximo_aniversario

    @staticmethod
    def verificar_reajustes(db: Session) -> Dict[str, Any]:
        """
        Verifica os contratos que terão reajuste no próximo mês.
        
        Returns:
            Dicionário com informações sobre os contratos com reajuste próximo
        """
        # Buscar todos os clientes ativos que têm data de início definida
        clientes = db.query(Client).filter(
            Client.is_active == True,
            Client.start_date.isnot(None)
        ).all()
        
        if not clientes:
            return {
                "total": 0,
                "contratos_reajuste": [],
                "message": "Nenhum cliente com data de início definida."
            }
        
        hoje = datetime.now().date()
        proximo_mes = (hoje + relativedelta(months=1))
        
        contratos_reajuste = []
        
        for cliente in clientes:
            if not cliente.start_date:
                continue
                
            # Calcula a próxima data de reajuste
            proximo_reajuste = ClientService.calcular_proximo_reajuste(
                cliente.start_date
            )
            
            # Verifica se o reajuste é no próximo mês
            if (proximo_reajuste and 
                proximo_reajuste.month == proximo_mes.month and 
                proximo_reajuste.year == proximo_mes.year):
                
                # Adiciona o cliente à lista de reajustes próximos
                contratos_reajuste.append({
                    "id": cliente.id,
                    "name": cliente.name,
                    "start_date": cliente.start_date.isoformat(),
                    "next_adjustment": proximo_reajuste.isoformat(),
                    "owner_id": cliente.owner_id
                })
                
                # Atualizamos as observações do cliente para incluir reajuste
                notes = cliente.notes or ""
                if "REAJUSTE" not in notes:
                    if notes:
                        notes = f"{notes}; REAJUSTE"
                    else:
                        notes = "REAJUSTE"
                    
                    cliente.notes = notes
                    db.commit()
        
        return {
            "total": len(contratos_reajuste),
            "contratos_reajuste": contratos_reajuste,
            "message": (
                f"Encontrados {len(contratos_reajuste)} contratos " 
                f"com reajuste em {proximo_mes.month}/{proximo_mes.year}."
            )
        }
