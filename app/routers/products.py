# app/routers/products.py
#
# Define el endpoint para la ingesta de datos de productos.

from fastapi import APIRouter, HTTPException, status
from app.models.products import ProductsData
from app.services.products import ingest_products_data
import logging

# Crea una instancia de APIRouter.
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def ingest_products(products_data: ProductsData):
    """
    Ingesta un conjunto de registros de productos.
    """
    try:
        ingest_products_data(products_data)
        return {"message": "Products data ingested successfully."}
    except Exception as e:
        logging.error(f"Error in products ingestion endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
