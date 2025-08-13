# app/routers/sales.py
#
# Define el endpoint para la ingesta de datos de ventas.

from fastapi import APIRouter, HTTPException, status
from app.models.sales import SalesData
from app.services.sales import ingest_sales_data
import logging

# Crea una instancia de APIRouter.
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def ingest_sales(sales_data: SalesData):
    """
    Ingesta un conjunto de registros de ventas.
    """
    try:
        ingest_sales_data(sales_data)
        return {"message": "Sales data ingested successfully."}
    except Exception as e:
        logging.error(f"Error in sales ingestion endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
