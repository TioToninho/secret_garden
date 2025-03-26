#!/usr/bin/env python3
import argparse

from src.secret_garden.cli.db_viewer import main as db_viewer_main
from src.secret_garden.cli.sqlite_viewer import main as sqlite_viewer_main


def main():
    parser = argparse.ArgumentParser(
        description='Ferramentas de linha de comando para o Secret Garden'
    )
    subparsers = parser.add_subparsers(
        dest='command', help='Comandos disponíveis'
    )

    # Comando para gerenciar clientes
    client_parser = subparsers.add_parser('client', help='Gerenciar clientes')
    client_parser.set_defaults(func=db_viewer_main)

    # Comando para visualizar o banco de dados SQLite
    db_parser = subparsers.add_parser(
        'db', help='Visualizar banco de dados SQLite'
    )
    db_parser.set_defaults(func=sqlite_viewer_main)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # Não remover o comando principal dos argumentos
        # Apenas executar a função correspondente
        args.func()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
