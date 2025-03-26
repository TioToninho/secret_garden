# Scripts de Utilitários

Este diretório contém scripts de utilitários para o projeto Secret Garden.

## Scripts de Banco de Dados

Os scripts relacionados ao banco de dados estão localizados no diretório `database/`:

- `db_reset.py`: Script para resetar o banco de dados SQLite e criar as tabelas.
- `db_tools.py`: Ferramentas para gerenciar o banco de dados, incluindo consultas e manipulação de dados.
- `close_connections.py`: Script para fechar todas as conexões com o banco de dados SQLite.
- `update_schema.py`: Script para atualizar o esquema do banco de dados, adicionando novas tabelas.

## Uso

Para usar esses scripts, navegue até a pasta raiz do projeto e execute:

```bash
# Resetar o banco de dados
python scripts/database/db_reset.py

# Ferramentas de banco de dados
python scripts/database/db_tools.py client list
python scripts/database/db_tools.py db tables

# Fechar conexões com o banco de dados
python scripts/database/close_connections.py

# Atualizar o esquema do banco de dados (criar novas tabelas)
python scripts/database/update_schema.py

# Atualizar o esquema do banco de dados e recriar todas as tabelas 
# (CUIDADO: isto apagará todos os dados das tabelas)
python scripts/database/update_schema.py --recreate
``` 