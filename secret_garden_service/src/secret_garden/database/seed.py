from datetime import date, datetime

from sqlalchemy.orm import Session

from src.secret_garden.database.config import SessionLocal
from src.secret_garden.database.models import Client, Owner


def seed_owners(db: Session):
    """Adiciona proprietários de exemplo ao banco de dados"""
    # Verifica se já existem proprietários
    existing_owners = db.query(Owner).count()
    if existing_owners > 0:
        print('Banco de dados já possui proprietários. Pulando seed.')
        return

    # Proprietários de exemplo
    owners = [
        Owner(name='João Silva'),
        Owner(name='Maria Oliveira'),
        Owner(name='Carlos Santos'),
        Owner(name='Ana Pereira'),
    ]

    # Adiciona os proprietários ao banco de dados
    for owner in owners:
        db.add(owner)

    db.commit()
    print(
        f'Adicionados {len(owners)} proprietários de exemplo ao banco de dados.'
    )


def seed_clients(db: Session):
    """Adiciona clientes de exemplo ao banco de dados"""
    # Verifica se já existem clientes
    existing_clients = db.query(Client).count()
    if existing_clients > 0:
        print('Banco de dados já possui clientes. Pulando seed.')
        return

    # Verificar se existem proprietários
    owners = db.query(Owner).all()
    if not owners:
        print(
            'Não existem proprietários. Executando seed de proprietários primeiro.'
        )
        seed_owners(db)
        owners = db.query(Owner).all()

    # Clientes de exemplo
    clients = [
        Client(
            name='Empresa A',
            owner_id=owners[0].id,
            status='Ativo',
            due_date=10,
            amount_paid=1500.00,
            property_tax=200.00,
            interest=0.00,
            utilities=150.00,
            insurance=50.00,
            condo_fee=300.00,
            percentage=10.0,
            delivery_fee=15.00,
            start_date=date(2023, 1, 1),
            condo_paid=True,
            withdrawal_date=date(2023, 3, 15),
            withdrawal_number='12345',
            payment_date=date(2023, 3, 10),
            notes='Cliente pontual',
            has_monthly_variation=True,
            is_active=True,
            created_at=datetime.now(),
        ),
        Client(
            name='Empresa B',
            owner_id=owners[0].id,
            status='Ativo',
            due_date=15,
            amount_paid=2000.00,
            property_tax=250.00,
            interest=0.00,
            utilities=200.00,
            insurance=75.00,
            condo_fee=400.00,
            percentage=8.0,
            delivery_fee=15.00,
            start_date=date(2023, 2, 1),
            condo_paid=True,
            withdrawal_date=date(2023, 3, 20),
            withdrawal_number='12346',
            payment_date=date(2023, 3, 15),
            notes='Contrato renovado recentemente',
            has_monthly_variation=False,
            is_active=True,
            created_at=datetime.now(),
        ),
        Client(
            name='Empresa C',
            owner_id=owners[1].id,
            status='Ativo',
            due_date=20,
            amount_paid=1800.00,
            property_tax=220.00,
            interest=10.00,
            utilities=180.00,
            insurance=60.00,
            condo_fee=350.00,
            percentage=9.0,
            delivery_fee=15.00,
            start_date=date(2022, 10, 1),
            condo_paid=False,
            withdrawal_date=date(2023, 3, 25),
            withdrawal_number='12347',
            payment_date=date(2023, 3, 22),
            notes='Pagamento com atraso frequente',
            has_monthly_variation=True,
            is_active=True,
            created_at=datetime.now(),
        ),
        Client(
            name='Empresa D',
            owner_id=owners[2].id,
            status='Inativo',
            due_date=5,
            amount_paid=1200.00,
            property_tax=180.00,
            interest=0.00,
            utilities=120.00,
            insurance=40.00,
            condo_fee=250.00,
            percentage=7.0,
            delivery_fee=15.00,
            start_date=date(2022, 5, 1),
            condo_paid=True,
            withdrawal_date=date(2023, 2, 10),
            withdrawal_number='12348',
            payment_date=date(2023, 2, 5),
            notes='Contrato encerrado',
            has_monthly_variation=False,
            is_active=False,
            created_at=datetime.now(),
        ),
    ]

    # Adiciona os clientes ao banco de dados
    for client in clients:
        db.add(client)

    db.commit()
    print(f'Adicionados {len(clients)} clientes de exemplo ao banco de dados.')


def seed_database():
    """Inicializa o banco de dados com dados de exemplo"""
    db = SessionLocal()
    try:
        seed_owners(db)
        seed_clients(db)
    finally:
        db.close()


if __name__ == '__main__':
    seed_database()
