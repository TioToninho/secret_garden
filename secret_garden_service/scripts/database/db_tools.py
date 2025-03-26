#!/usr/bin/env python3
"""
Ferramentas para gerenciar o banco de dados do Secret Garden.

Uso:
    python db_tools.py client list
    python db_tools.py client view 1
    python db_tools.py client add --name "Novo Cliente" --owner-id 1 \
        --status "Ativo"
    python db_tools.py client delete 1 --soft

    python db_tools.py db tables
    python db_tools.py db describe clients
    python db_tools.py db query clients --limit 5 --where "is_active=1"
    python db_tools.py db sql "SELECT * FROM clients \
        WHERE name LIKE '%Empresa%'"
"""

import os
import sys

# Adicionar o diretório raiz ao path para permitir importações relativas
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'client':
            from src.secret_garden.cli.db_viewer import main

            # Remover o primeiro argumento (db_tools.py) e manter o resto
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            main()
        elif sys.argv[1] == 'db':
            from src.secret_garden.cli.sqlite_viewer import main

            # Remover o primeiro argumento (db_tools.py) e manter o resto
            sys.argv = [sys.argv[0]] + sys.argv[2:]
            main()
        else:
            print(f'Comando desconhecido: {sys.argv[1]}')
            print('Comandos disponíveis: client, db')
            sys.exit(1)
    else:
        print('Uso: python db_tools.py {client|db} [opções]')
        print(
            "Execute 'python db_tools.py client -h' ou "
            "'python db_tools.py db -h' para mais informações."
        )
        sys.exit(1)
