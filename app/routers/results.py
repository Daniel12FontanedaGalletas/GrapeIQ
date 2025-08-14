# app/routers/results.py
#
# Este archivo define el endpoint de la API para consultar los resultados
# de los pronósticos generados por el job.

import os
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
import psycopg2
from typing import List, Dict, Any

# Se crea una instancia de APIRouter para que pueda ser importada por main.py.
router = APIRouter()

# Obtener la clave secreta de las variables de entorno.
FORECAST_SECRET = os.environ.get("FORECAST_SECRET", "super-secret-key-123")
# Configuración de la base de datos
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

def verify_secret(secret: str) -> bool:
    """
    Verifica que la clave secreta proporcionada coincida.
    """
    return secret == FORECAST_SECRET

@router.get("/forecast/results/{tenant_id}")
async def get_forecast_results(
    tenant_id: UUID,
    secret: str
) -> List[Dict[str, Any]]:
    """
    Endpoint para obtener los resultados del pronóstico para un cliente (tenant) específico.
    
    Este endpoint está protegido por una clave secreta.
    
    - **tenant_id**: El ID del cliente para el cual se obtendrán los pronósticos.
    - **secret**: La clave secreta para autenticar la petición.
    """
    if not verify_secret(secret):
        raise HTTPException(status_code=403, detail="Acceso denegado: Clave secreta inválida.")
    
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Consultar los pronósticos para el tenant_id dado
        cursor.execute(
            "SELECT sku, date, predicted_qty, model_used FROM forecasts WHERE tenant_id = %s ORDER BY date, sku",
            (str(tenant_id),)
        )
        records = cursor.fetchall()

        if not records:
            raise HTTPException(status_code=404, detail=f"No se encontraron pronósticos para el cliente con ID: {tenant_id}")
            
        # Formatear los resultados en una lista de diccionarios
        forecast_results = [
            {
                "sku": record[0],
                "date": record[1].isoformat(),
                "predicted_qty": float(record[2]),
                "model_used": record[3]
            }
            for record in records
        ]
        
        return forecast_results
        
    except Exception as e:
        # En caso de error, devolver un error 500 con los detalles
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {e}"
        )
    finally:
        if conn:
            conn.close()
