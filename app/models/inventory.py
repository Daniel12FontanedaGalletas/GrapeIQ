# app/models/inventory.py
#
# Define los modelos de datos para los registros de inventario.
# Se usa Pydantic para validar los datos que entran a la API.

from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import date # ¡Nueva importación!

class InventoryRecord(BaseModel):
    """
    Representa un solo registro de inventario para un producto y una fecha.
    """
    date: date # ¡Cambio clave aquí! Ahora Pydantic valida el formato de la fecha.
    sku: str   # El Stock Keeping Unit del producto.
    qty: int   # La cantidad de productos en stock.
    location: str # La ubicación del inventario (ej. "almacén central").

class InventoryData(BaseModel):
    """
    Representa el cuerpo de la petición para la ingesta de inventario.
    """
    tenant_id: UUID
    data: List[InventoryRecord]
