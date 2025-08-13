# app/models/sales.py
#
# Define el modelo de datos para la ingesta de ventas usando Pydantic.
# Pydantic nos ayuda a validar que los datos que recibimos tienen el formato correcto.

from datetime import date
from pydantic import BaseModel
from typing import List
import uuid

class SalesRecord(BaseModel):
    """Modelo de Pydantic para un solo registro de venta."""
    # `date` asegura que el campo sea un objeto de fecha válido.
    date: date
    # `sku` (Stock Keeping Unit) es una cadena de texto.
    sku: str
    # `qty` (cantidad) debe ser un número entero.
    qty: int
    # `price` (precio) debe ser un número decimal.
    price: float
    # `channel` (canal de venta) es una cadena de texto.
    channel: str

class SalesData(BaseModel):
    """
    Modelo de Pydantic para la ingesta de múltiples registros de venta.
    El `tenant_id` es necesario para la seguridad a nivel de fila (RLS).
    """
    # `tenant_id` es un identificador único del inquilino.
    tenant_id: uuid.UUID
    # `data` es una lista de objetos `SalesRecord`.
    data: List[SalesRecord]
