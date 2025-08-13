# app/routers/inventory.py
#
# Define el endpoint para la ingesta de datos de inventario.

from fastapi import APIRouter, HTTPException, status
from app.models.inventory import InventoryData
from app.services.inventory import ingest_inventory_data
import logging

# Crea una instancia de APIRouter.
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def ingest_inventory(inventory_data: InventoryData):
    """
    Ingesta un conjunto de registros de inventario.
    """
    try:
        ingest_inventory_data(inventory_data)
        return {"message": "Inventory data ingested successfully."}
    except Exception as e:
        logging.error(f"Error in inventory ingestion endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
