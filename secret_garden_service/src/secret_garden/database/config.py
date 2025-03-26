import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o banco de dados SQLite
# Usar um caminho absoluto para o arquivo do banco de dados
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
db_path = os.path.join(basedir, 'src', 'data', 'secret_garden.db')
SQLALCHEMY_DATABASE_URL = f'sqlite:///{db_path}'

# Criação do engine do SQLAlchemy
# Para SQLite, é necessário adicionar o parâmetro connect_args
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

# Criação da sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


# Função para obter uma sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
