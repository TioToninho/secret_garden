from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.secret_garden.database.init_db import init_db

from .routers import (
    clients, health, monthly_calculations, owners,
    monthly_variable_values, monthly_transfers, bank_returns
)

# Inicializa o banco de dados
init_db()

app = FastAPI(title='Secret Garden API')

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health.router)
app.include_router(clients.router)
app.include_router(monthly_calculations.router)
app.include_router(owners.router)
app.include_router(monthly_variable_values.router)
app.include_router(monthly_transfers.router)
app.include_router(bank_returns.router)
