# app/routers/data.py

from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_db_connection # Usamos la nueva dependencia
from app.services.analytics import (
    get_total_sales_for_tenant, 
    get_total_inventory_for_tenant,
    get_sales_by_channel_for_tenant,
    get_total_inventory_value_for_tenant
)
from app.services.auth import oauth2_scheme, verify_token
import logging
from uuid import UUID
import psycopg2 # Necesario para el type hinting de la conexión

# Crea una instancia de APIRouter.
router = APIRouter()

# --- NOTA IMPORTANTE ---
# Para que los endpoints de analytics funcionen, deberás actualizar las funciones 
# en `app/services/analytics.py` para que acepten `conn` como primer argumento.
# Por ejemplo: def get_total_sales_for_tenant(conn, tenant_id: UUID):
# -------------------------

@router.get("/sales/{tenant_id}", status_code=status.HTTP_200_OK)
def get_sales_data(
    tenant_id: UUID, 
    token: str = Depends(oauth2_scheme),
    conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Obtiene todos los registros de ventas para un `tenant_id` específico.
    Requiere un token de autenticación y usa una conexión del pool.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        with conn.cursor() as cur:
            query = "SELECT date, sku, qty, price, channel, tenant_id FROM sales WHERE tenant_id = %s;"
            cur.execute(query, (str(tenant_id),))
            records = cur.fetchall()
            
            sales_records = [
                {
                    "date": record[0], "sku": record[1], "qty": record[2],
                    "price": record[3], "channel": record[4], "tenant_id": record[5]
                }
                for record in records
            ]
            return {"data": sales_records}

    except Exception as e:
        logging.error(f"Error while retrieving sales data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/products/{tenant_id}", status_code=status.HTTP_200_OK)
def get_products_data(
    tenant_id: UUID, 
    token: str = Depends(oauth2_scheme),
    conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Obtiene todos los registros de productos para un `tenant_id` específico.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        with conn.cursor() as cur:
            query = "SELECT sku, name, category, price, description, tenant_id FROM products WHERE tenant_id = %s;"
            cur.execute(query, (str(tenant_id),))
            records = cur.fetchall()
            
            products_records = [
                {
                    "sku": record[0], "name": record[1], "category": record[2],
                    "price": record[3], "description": record[4], "tenant_id": record[5]
                }
                for record in records
            ]
            return {"data": products_records}

    except Exception as e:
        logging.error(f"Error while retrieving products data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
@router.get("/inventory/{tenant_id}", status_code=status.HTTP_200_OK)
def get_inventory_data(
    tenant_id: UUID, 
    token: str = Depends(oauth2_scheme),
    conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Obtiene todos los registros de inventario para un `tenant_id` específico.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        with conn.cursor() as cur:
            query = "SELECT date, sku, qty, location, tenant_id FROM inventory WHERE tenant_id = %s;"
            cur.execute(query, (str(tenant_id),))
            records = cur.fetchall()

            inventory_records = [
                {
                    "date": record[0], "sku": record[1], "qty": record[2],
                    "location": record[3], "tenant_id": record[4]
                }
                for record in records
            ]
            return {"data": inventory_records}

    except Exception as e:
        logging.error(f"Error while retrieving inventory data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/total_sales/{tenant_id}", status_code=status.HTTP_200_OK)
def get_total_sales(
    tenant_id: UUID, 
    token: str = Depends(oauth2_scheme),
    conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Endpoint para obtener las ventas totales de un cliente.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        total_sales = get_total_sales_for_tenant(conn, tenant_id)
        return {"total_sales": total_sales}
    except Exception as e:
        logging.error(f"Error in total sales analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/total_inventory/{tenant_id}", status_code=status.HTTP_200_OK)
def get_total_inventory(
    tenant_id: UUID, 
    token: str = Depends(oauth2_scheme),
    conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Endpoint para obtener el inventario total de un cliente.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        total_inventory = get_total_inventory_for_tenant(conn, tenant_id)
        return {"total_inventory": total_inventory}
    except Exception as e:
        logging.error(f"Error in total inventory analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/sales_by_channel/{tenant_id}", status_code=status.HTTP_200_OK)
def get_sales_by_channel(
    tenant_id: UUID, 
    token: str = Depends(oauth2_scheme),
    conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Endpoint para obtener las ventas por canal de un cliente.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        sales_by_channel = get_sales_by_channel_for_tenant(conn, tenant_id)
        return {"sales_by_channel": sales_by_channel}
    except Exception as e:
        logging.error(f"Error in sales by channel analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/total_inventory_value/{tenant_id}", status_code=status.HTTP_200_OK)
def get_total_inventory_value(
    tenant_id: UUID, 
    token: str = Depends(oauth2_scheme),
    conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    """
    Endpoint para obtener el valor total del inventario de un cliente.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        total_value = get_total_inventory_value_for_tenant(conn, tenant_id)
        return {"total_inventory_value": total_value}
    except Exception as e:
        logging.error(f"Error in total inventory value analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )