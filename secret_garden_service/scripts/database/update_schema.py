#!/usr/bin/env python3
"""
Script para atualizar o esquema do banco de dados, adicionando novas tabelas.
"""

import argparse
import os
import sys

# Adicionar o diretório raiz ao path para permitir importações relativas
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable, DropTable

from src.secret_garden.database.config import SQLALCHEMY_DATABASE_URL, Base
from src.secret_garden.database.models import Client, MonthlyCalculation, Owner


def get_db_path():
    """Extrai o caminho do banco de dados da URL SQLAlchemy"""
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite:///'):
        return SQLALCHEMY_DATABASE_URL[10:]
    return None


def update_database_schema(recreate=False):
    """
    Atualiza o esquema do banco de dados, adicionando novas tabelas

    Args:
        recreate: Se True, recria as tabelas existentes (Drop + Create)
    """
    db_path = get_db_path()

    if not db_path:
        print('Erro: Não foi possível determinar o caminho do banco de dados.')
        return

    if not os.path.exists(db_path):
        print(f'Aviso: Banco de dados não encontrado em: {db_path}')
        print('Criando novo banco de dados...')

    # Criar engine SQLAlchemy
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # Verificar se as tabelas existem
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    print('Tabelas existentes:', existing_tables)

    # Lista de tabelas a serem gerenciadas
    tables = [
        Owner.__tablename__,
        Client.__tablename__,
        MonthlyCalculation.__tablename__,
    ]

    if recreate:
        # Recriar tabelas existentes (aplicar novas configurações)
        for table_name in tables:
            if table_name in existing_tables:
                print(f'Recriando tabela: {table_name}')

                # Criar sessão
                Session = sessionmaker(bind=engine)
                session = Session()

                # Obter schema da tabela
                table = Base.metadata.tables[table_name]

                # Executar DDL para dropar e recriar a tabela
                session.execute(DropTable(table))
                session.execute(CreateTable(table))
                session.commit()
                session.close()

                print(f'Tabela {table_name} recriada com sucesso')

    # Criar tabelas que não existem
    for table_name in tables:
        if table_name not in existing_tables:
            print(f'Criando tabela: {table_name}')
            Base.metadata.tables[table_name].create(bind=engine)
        elif not recreate:
            print(f'Tabela já existe: {table_name}')

    print('Esquema do banco de dados atualizado com sucesso!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Atualiza o esquema do banco de dados'
    )
    parser.add_argument(
        '--recreate',
        action='store_true',
        help='Recriar as tabelas existentes (vai apagar todos os dados)',
    )
    args = parser.parse_args()

    if args.recreate:
        print(
            '⚠️ ATENÇÃO: Esta operação vai recriar todas as tabelas e apagar todos os dados!'
        )
        confirm = input("Digite 'sim' para confirmar: ")
        if confirm.lower() != 'sim':
            print('Operação cancelada pelo usuário.')
            sys.exit(0)

    update_database_schema(recreate=args.recreate)
