#!/usr/bin/env python3
import argparse
import os
import sqlite3

from tabulate import tabulate

from src.secret_garden.database.config import SQLALCHEMY_DATABASE_URL


def get_db_path():
    """Extrai o caminho do banco de dados da URL SQLAlchemy"""
    # A URL SQLAlchemy é algo como: sqlite:///path/to/database.db
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite:///'):
        return SQLALCHEMY_DATABASE_URL[10:]
    return None


def list_tables(conn):
    """Lista todas as tabelas no banco de dados"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print('Nenhuma tabela encontrada no banco de dados.')
        return

    print('Tabelas disponíveis:')
    for table in tables:
        print(f'- {table[0]}')


def describe_table(conn, table_name):
    """Descreve a estrutura de uma tabela"""
    cursor = conn.cursor()
    try:
        cursor.execute(f'PRAGMA table_info({table_name});')
        columns = cursor.fetchall()

        if not columns:
            print(f"Tabela '{table_name}' não encontrada.")
            return

        headers = ['ID', 'Nome', 'Tipo', 'NotNull', 'Default', 'PK']
        rows = []

        for col in columns:
            rows.append([col[0], col[1], col[2], col[3], col[4], col[5]])

        print(f"Estrutura da tabela '{table_name}':")
        print(tabulate(rows, headers=headers, tablefmt='grid'))

    except sqlite3.Error as e:
        print(f'Erro ao descrever tabela: {e}')


def query_table(conn, table_name, limit=10, where=None, order_by=None):
    """Consulta dados de uma tabela"""
    cursor = conn.cursor()
    try:
        # Construir a consulta SQL
        query = f'SELECT * FROM {table_name}'

        if where:
            query += f' WHERE {where}'

        if order_by:
            query += f' ORDER BY {order_by}'

        query += f' LIMIT {limit}'

        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print(f"Nenhum registro encontrado na tabela '{table_name}'.")
            return

        # Obter nomes das colunas
        cursor.execute(f'PRAGMA table_info({table_name});')
        columns = cursor.fetchall()
        headers = [col[1] for col in columns]

        print(f"Dados da tabela '{table_name}':")
        print(tabulate(rows, headers=headers, tablefmt='grid'))

    except sqlite3.Error as e:
        print(f'Erro ao consultar tabela: {e}')


def execute_sql(conn, sql):
    """Executa uma consulta SQL personalizada"""
    cursor = conn.cursor()
    try:
        cursor.execute(sql)

        if sql.strip().upper().startswith(('SELECT', 'PRAGMA')):
            rows = cursor.fetchall()

            if not rows:
                print('A consulta não retornou resultados.')
                return

            # Tentar obter nomes das colunas
            headers = [description[0] for description in cursor.description]

            print('Resultado da consulta:')
            print(tabulate(rows, headers=headers, tablefmt='grid'))
        else:
            conn.commit()
            print(
                f'Comando executado com sucesso. Linhas afetadas: {cursor.rowcount}'
            )

    except sqlite3.Error as e:
        print(f'Erro ao executar SQL: {e}')


def main():
    parser = argparse.ArgumentParser(
        description='Ferramenta para visualizar e manipular o banco de dados SQLite'
    )
    subparsers = parser.add_subparsers(
        dest='command', help='Comandos disponíveis'
    )

    # Comando para listar tabelas
    subparsers.add_parser('tables', help='Listar todas as tabelas')

    # Comando para descrever uma tabela
    describe_parser = subparsers.add_parser(
        'describe', help='Descrever estrutura de uma tabela'
    )
    describe_parser.add_argument('table', help='Nome da tabela')

    # Comando para consultar dados
    query_parser = subparsers.add_parser(
        'query', help='Consultar dados de uma tabela'
    )
    query_parser.add_argument('table', help='Nome da tabela')
    query_parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Limite de registros (padrão: 10)',
    )
    query_parser.add_argument('--where', help='Condição WHERE')
    query_parser.add_argument('--order-by', help='Ordenação ORDER BY')

    # Comando para executar SQL personalizado
    sql_parser = subparsers.add_parser(
        'sql', help='Executar SQL personalizado'
    )
    sql_parser.add_argument('query', help='Consulta SQL a ser executada')

    args = parser.parse_args()

    # Obter caminho do banco de dados
    db_path = get_db_path()
    if not db_path:
        print('Erro: Não foi possível determinar o caminho do banco de dados.')
        return

    if not os.path.exists(db_path):
        print(f'Erro: Banco de dados não encontrado em: {db_path}')
        return

    # Conectar ao banco de dados
    try:
        conn = sqlite3.connect(db_path)

        # Executar o comando apropriado
        if args.command == 'tables':
            list_tables(conn)
        elif args.command == 'describe':
            describe_table(conn, args.table)
        elif args.command == 'query':
            query_table(
                conn, args.table, args.limit, args.where, args.order_by
            )
        elif args.command == 'sql':
            execute_sql(conn, args.query)
        else:
            parser.print_help()

        conn.close()

    except sqlite3.Error as e:
        print(f'Erro ao conectar ao banco de dados: {e}')


if __name__ == '__main__':
    main()
