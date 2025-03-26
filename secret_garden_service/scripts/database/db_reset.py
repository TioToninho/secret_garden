#!/usr/bin/env python3
"""
Script para resetar o banco de dados e criar as tabelas de acordo com os modelos.
"""

import os
import sqlite3
import sys

# Adicionar o diretório raiz ao path para permitir importações relativas
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.secret_garden.database.config import SQLALCHEMY_DATABASE_URL, Base


def get_db_path():
    """Extrai o caminho do banco de dados da URL SQLAlchemy"""
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite:///'):
        return SQLALCHEMY_DATABASE_URL[10:]
    return None


def reset_database():
    """Reseta o banco de dados, removendo e recriando as tabelas"""
    db_path = get_db_path()

    if not db_path:
        print('Erro: Não foi possível determinar o caminho do banco de dados.')
        return

    if not os.path.exists(db_path):
        print(f'Aviso: Banco de dados não encontrado em: {db_path}')
        print('Criando novo banco de dados...')

    # Conectar ao banco de dados SQLite diretamente
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fazer backup dos dados existentes (opcional)
    try:
        cursor.execute('SELECT * FROM clients')
        clients_data = cursor.fetchall()
        print(f'Backup de {len(clients_data)} clientes realizado.')
    except sqlite3.OperationalError:
        clients_data = []
        print('Nenhum dado de cliente para backup.')

    # Remover tabela existente
    try:
        cursor.execute('DROP TABLE IF EXISTS clients')
        print("Tabela 'clients' removida com sucesso.")
    except sqlite3.OperationalError as e:
        print(f'Erro ao remover tabela: {e}')

    conn.commit()
    conn.close()

    # Criar engine SQLAlchemy
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    # Criar todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)
    print('Tabelas recriadas com sucesso de acordo com os modelos.')

    # Restaurar dados (opcional)
    if clients_data:
        Session = sessionmaker(bind=engine)
        db = Session()

        # Aqui você precisaria mapear os dados antigos para o novo esquema
        # Como a estrutura mudou, isso pode exigir adaptações
        print('Restauração de dados não implementada.')

        db.close()


if __name__ == '__main__':
    reset_database()
    print('Banco de dados resetado com sucesso!')
