# app/routers/forecast.py
#
# Este archivo define el endpoint de la API para iniciar el job de pronóstico.
# Se ha corregido para incluir una instancia de APIRouter.

import os
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import ValidationError

from app.jobs.forecast.job import run_forecast_job

# =============================================================================
# Corrección del error de importación.
# Se crea una instancia de APIRouter y se le asigna a la variable 'router'
# para que pueda ser importada por main.py.
# =============================================================================
router = APIRouter()

# Obtener la clave secreta de las variables de entorno.
FORECAST_SECRET = os.environ.get("FORECAST_SECRET", "super-secret-key-123")

def verify_secret(secret: str) -> bool:
    """
    Verifica que la clave secreta proporcionada coincida.
    """
    return secret == FORECAST_SECRET

@router.post("/forecast/run")
async def run_forecast(
    tenant_id: UUID,
    secret: str,
    background_tasks: BackgroundTasks
):
    """
    Endpoint para iniciar el job de pronóstico para un cliente (tenant) específico.
    
    Este endpoint está protegido por una clave secreta. El job se ejecuta
    como una tarea de fondo para no bloquear la respuesta de la API.
    
    - **tenant_id**: El ID del cliente para el cual se ejecutará el pronóstico.
    - **secret**: La clave secreta para autenticar la petición.
    """
    if not verify_secret(secret):
        raise HTTPException(status_code=403, detail="Acceso denegado: Clave secreta inválida.")
        
    try:
        # Añade la función del job a las tareas de fondo.
        background_tasks.add_task(run_forecast_job, tenant_id=tenant_id)
        
        return {"message": "Job de pronóstico iniciado en segundo plano."}
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Error de validación: {e.errors()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {e}"
        )
