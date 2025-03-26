from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.secret_garden.api.routers import (
    clients, owners, monthly_calculations, retornos, health
)
from src.secret_garden.database.config import init_db

# Iniciar o banco de dados
init_db()

app = FastAPI(
    title="Secret Garden API",
    description=(
        "API para gerenciar clientes, proprietários e cálculos financeiros"
    ),
    version="0.1.0"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir as rotas
app.include_router(clients.router)
app.include_router(owners.router)
app.include_router(monthly_calculations.router)
app.include_router(retornos.router)
app.include_router(health.router)

@app.get("/")
def read_root():
    return {
        "message": "Bem-vindo à API do Secret Garden",
        "docs": "/docs"
    } 