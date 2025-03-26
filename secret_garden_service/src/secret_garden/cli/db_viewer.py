import argparse
from datetime import datetime

from tabulate import tabulate

from src.secret_garden.database.config import SessionLocal
from src.secret_garden.database.models import Client


def list_clients(args):
    """Lista todos os clientes no banco de dados"""
    db = SessionLocal()
    try:
        query = db.query(Client)

        # Aplicar filtros se fornecidos
        if args.active is not None:
            query = query.filter(Client.is_active == args.active)
        if args.owner_id:
            query = query.filter(Client.owner_id == args.owner_id)

        clients = query.all()

        if not clients:
            print('Nenhum cliente encontrado.')
            return

        # Preparar dados para exibição em tabela
        headers = [
            'ID',
            'Locatário',
            'Proprietário',
            'Situação',
            'Vencimento',
            'Valor Pago',
        ]
        rows = []

        for client in clients:
            rows.append(
                [
                    client.id,
                    client.name,
                    client.owner_id,
                    client.status,
                    client.due_date,
                    client.amount_paid,
                ]
            )

        print(tabulate(rows, headers=headers, tablefmt='grid'))
        print(f'Total de clientes: {len(clients)}')

    finally:
        db.close()


def view_client(args):
    """Visualiza detalhes de um cliente específico"""
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == args.id).first()

        if not client:
            print(f'Cliente com ID {args.id} não encontrado.')
            return

        # Exibir todos os detalhes do cliente
        client_dict = {
            c.name: getattr(client, c.name) for c in client.__table__.columns
        }

        # Formatar para exibição
        rows = [[k, v] for k, v in client_dict.items()]
        print(tabulate(rows, headers=['Campo', 'Valor'], tablefmt='grid'))

    finally:
        db.close()


def add_client(args):
    """Adiciona um novo cliente ao banco de dados"""
    db = SessionLocal()
    try:
        # Criar cliente com dados mínimos obrigatórios
        new_client = Client(
            name=args.name,
            owner_id=args.owner_id,
            status=args.status or 'Ativo',
            created_at=datetime.now(),
        )

        # Adicionar campos opcionais se fornecidos
        if args.due_date:
            new_client.due_date = args.due_date
        if args.amount_paid:
            new_client.amount_paid = args.amount_paid
        if args.notes:
            new_client.notes = args.notes

        db.add(new_client)
        db.commit()
        db.refresh(new_client)

        print(f'Cliente adicionado com sucesso! ID: {new_client.id}')

    finally:
        db.close()


def delete_client(args):
    """Exclui um cliente do banco de dados (exclusão física)"""
    db = SessionLocal()
    try:
        client = db.query(Client).filter(Client.id == args.id).first()

        if not client:
            print(f'Cliente com ID {args.id} não encontrado.')
            return

        if not args.force and args.soft:
            # Soft delete (apenas marca como inativo)
            client.is_active = False
            client.updated_at = datetime.now()
            db.commit()
            print(f'Cliente com ID {args.id} marcado como inativo.')
        elif args.force or not args.soft:
            # Hard delete (remove do banco)
            db.delete(client)
            db.commit()
            print(
                f'Cliente com ID {args.id} removido permanentemente do banco de dados.'
            )

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description='Ferramenta de linha de comando para gerenciar clientes'
    )
    subparsers = parser.add_subparsers(
        dest='command', help='Comandos disponíveis'
    )

    # Comando para listar clientes
    list_parser = subparsers.add_parser('list', help='Listar clientes')
    list_parser.add_argument(
        '--active',
        type=lambda x: x.lower() == 'true',
        help='Filtrar por clientes ativos (true/false)',
    )
    list_parser.add_argument(
        '--owner-id', type=int, help='Filtrar por ID do proprietário'
    )

    # Comando para visualizar um cliente
    view_parser = subparsers.add_parser(
        'view', help='Visualizar detalhes de um cliente'
    )
    view_parser.add_argument('id', type=int, help='ID do cliente')

    # Comando para adicionar um cliente
    add_parser = subparsers.add_parser('add', help='Adicionar um novo cliente')
    add_parser.add_argument(
        '--name', required=True, help='Nome do cliente (locatário)'
    )
    add_parser.add_argument(
        '--owner-id', type=int, required=True, help='ID do proprietário'
    )
    add_parser.add_argument('--status', help='Situação do cliente')
    add_parser.add_argument('--due-date', type=int, help='Dia de vencimento')
    add_parser.add_argument('--amount-paid', type=float, help='Valor pago')
    add_parser.add_argument('--notes', help='Observações')

    # Comando para excluir um cliente
    delete_parser = subparsers.add_parser('delete', help='Excluir um cliente')
    delete_parser.add_argument('id', type=int, help='ID do cliente')
    delete_parser.add_argument(
        '--force', action='store_true', help='Forçar exclusão permanente'
    )
    delete_parser.add_argument(
        '--soft',
        action='store_true',
        help='Realizar exclusão lógica (marcar como inativo)',
    )

    args = parser.parse_args()

    # Executar o comando apropriado
    if args.command == 'list':
        list_clients(args)
    elif args.command == 'view':
        view_client(args)
    elif args.command == 'add':
        add_client(args)
    elif args.command == 'delete':
        delete_client(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
