# app/models/products.py
#
# Define los modelos de datos para los productos usando Pydantic.
# Esto asegura que los datos que recibimos a través de la API sean válidos.

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class ProductRecord(BaseModel):
    """
    Representa un solo registro de producto.
    """
    sku: str
    name: str
    category: str
    price: float
    description: Optional[str] = None

class ProductsData(BaseModel):
    """
    Representa el cuerpo de la petición para la ingesta de productos.
    Incluye un tenant_id para el aislamiento de datos y una lista de registros.
    """
    tenant_id: UUID
    data: List[ProductRecord]
