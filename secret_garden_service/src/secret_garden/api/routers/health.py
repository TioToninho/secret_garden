from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import JSONResponse

from src.secret_garden.database.config import get_db

router = APIRouter(
    prefix="/api/health",
    tags=["health"],
)


@router.get("/", summary="Verificação básica de saúde")
async def health_check():
    """
    Verifica se a API está respondendo.
    
    Retorna um status 200 se a API estiver em funcionamento.
    """
    return {
        "status": "ok",
        "message": "Serviço funcionando normalmente"
    }


@router.get("/db", summary="Verificação da conexão com o banco de dados")
async def db_health_check(db: Session = Depends(get_db)):
    """
    Verifica se a conexão com o banco de dados está funcionando.
    
    Executa uma consulta simples para verificar se o banco de dados está acessível.
    """
    try:
        # Executa consulta SQL para verificar se o banco está respondendo
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {
                "status": "ok",
                "message": "Conexão com o banco de dados está funcionando"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Banco de dados retornou resultado inesperado"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na conexão com o banco de dados: {str(e)}"
        )


@router.get("/complete", summary="Verificação completa do sistema")
async def complete_health_check(db: Session = Depends(get_db)):
    """
    Verifica o estado de todos os componentes do sistema.
    
    Realiza uma verificação completa incluindo API e banco de dados.
    """
    health_status = {
        "api": {
            "status": "ok",
            "message": "API está funcionando corretamente"
        },
        "database": {
            "status": "error",
            "message": "Erro ao conectar com o banco de dados"
        },
        "overall": "error"
    }
    
    # Verificar banco de dados
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            health_status["database"] = {
                "status": "ok",
                "message": "Banco de dados está funcionando corretamente"
            }
    except Exception as e:
        health_status["database"] = {
            "status": "error",
            "message": f"Erro na conexão com o banco de dados: {str(e)}"
        }
    
    # Definir status geral com base nos componentes
    if (health_status["api"]["status"] == "ok" and
            health_status["database"]["status"] == "ok"):
        health_status["overall"] = "ok"
    else:
        health_status["overall"] = "error"
    
    # Se houver algum erro, retornar status 500
    if health_status["overall"] == "error":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=health_status
        )
    
    return health_status
