from src.secret_garden.database.config import Base, engine
# Importação necessária para que o SQLAlchemy reconheça o modelo
# ao criar as tabelas
from src.secret_garden.database.models import Client  # noqa
from src.secret_garden.database.seed import seed_database


def init_db():
    """Inicializa o banco de dados criando todas as tabelas"""
    Base.metadata.create_all(bind=engine)
    print('Banco de dados inicializado com sucesso!')

    # Adiciona dados de exemplo
    seed_database()


if __name__ == '__main__':
    init_db()
