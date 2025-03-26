#!/usr/bin/env python3
"""
Script para fechar todas as conexões com o banco de dados SQLite.
"""

import os
import sqlite3
import sys

# Adicionar o diretório raiz ao path para permitir importações relativas
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)

from src.secret_garden.database.config import SQLALCHEMY_DATABASE_URL


def get_db_path():
    """Extrai o caminho do banco de dados da URL SQLAlchemy"""
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite:///'):
        return SQLALCHEMY_DATABASE_URL[10:]
    return None


def close_connections():
    """Fecha todas as conexões com o banco de dados"""
    db_path = get_db_path()

    if not db_path:
        print('Erro: Não foi possível determinar o caminho do banco de dados.')
        return

    if not os.path.exists(db_path):
        print(f'Erro: Banco de dados não encontrado em: {db_path}')
        return

    try:
        # Tenta conectar ao banco de dados com modo exclusivo
        # Isso forçará o fechamento de outras conexões
        conn = sqlite3.connect(db_path, isolation_level='EXCLUSIVE')
        conn.execute('PRAGMA locking_mode = EXCLUSIVE')
        conn.execute('BEGIN EXCLUSIVE')

        # Libera todas as conexões
        conn.execute('PRAGMA optimize')
        conn.commit()
        conn.close()

        print('Todas as conexões com o banco de dados foram fechadas.')

    except sqlite3.OperationalError as e:
        print(f'Erro ao tentar fechar conexões: {e}')
        print(
            'Tente encerrar manualmente todos os processos que possam estar usando o banco.'
        )


if __name__ == '__main__':
    close_connections()
