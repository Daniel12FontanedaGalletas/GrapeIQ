# app/routers/data.py
#
# Este archivo define los endpoints para la consulta de datos.
# Ahora están protegidos y requieren un token de autenticación.

from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_db_connection
from app.services.analytics import (
    get_total_sales_for_tenant, 
    get_total_inventory_for_tenant,
    get_sales_by_channel_for_tenant,
    get_total_inventory_value_for_tenant  # ¡Nueva importación!
)
from app.services.auth import oauth2_scheme, verify_token
import logging
from uuid import UUID

# Crea una instancia de APIRouter.
router = APIRouter()

@router.get("/sales/{tenant_id}", status_code=status.HTTP_200_OK)
def get_sales_data(tenant_id: UUID, token: str = Depends(oauth2_scheme)):
    """
    Obtiene todos los registros de ventas para un `tenant_id` específico.
    Requiere un token de autenticación.
    """
    # Verifica el token y extrae la información del usuario
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        query = f"SELECT date, sku, qty, price, channel, tenant_id FROM sales WHERE tenant_id = '{tenant_id}';"
        cur.execute(query)
        records = cur.fetchall()
        
        sales_records = [
            {
                "date": record[0],
                "sku": record[1],
                "qty": record[2],
                "price": record[3],
                "channel": record[4],
                "tenant_id": record[5]
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
    finally:
        cur.close()
        conn.close()

@router.get("/products/{tenant_id}", status_code=status.HTTP_200_OK)
def get_products_data(tenant_id: UUID, token: str = Depends(oauth2_scheme)):
    """
    Obtiene todos los registros de productos para un `tenant_id` específico.
    Requiere un token de autenticación.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        query = f"SELECT sku, name, category, price, description, tenant_id FROM products WHERE tenant_id = '{tenant_id}';"
        cur.execute(query)
        records = cur.fetchall()
        
        products_records = [
            {
                "sku": record[0],
                "name": record[1],
                "category": record[2],
                "price": record[3],
                "description": record[4],
                "tenant_id": record[5]
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
    finally:
        cur.close()
        conn.close()
        
@router.get("/inventory/{tenant_id}", status_code=status.HTTP_200_OK)
def get_inventory_data(tenant_id: UUID, token: str = Depends(oauth2_scheme)):
    """
    Obtiene todos los registros de inventario para un `tenant_id` específico.
    Requiere un token de autenticación.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        query = f"SELECT date, sku, qty, location, tenant_id FROM inventory WHERE tenant_id = '{tenant_id}';"
        cur.execute(query)
        records = cur.fetchall()

        inventory_records = [
            {
                "date": record[0],
                "sku": record[1],
                "qty": record[2],
                "location": record[3],
                "tenant_id": record[4]
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
    finally:
        cur.close()
        conn.close()

@router.get("/analytics/total_sales/{tenant_id}", status_code=status.HTTP_200_OK)
def get_total_sales(tenant_id: UUID, token: str = Depends(oauth2_scheme)):
    """
    Endpoint para obtener las ventas totales de un cliente.
    Requiere un token de autenticación.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        total_sales = get_total_sales_for_tenant(tenant_id)
        return {"total_sales": total_sales}
    except Exception as e:
        logging.error(f"Error in total sales analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/total_inventory/{tenant_id}", status_code=status.HTTP_200_OK)
def get_total_inventory(tenant_id: UUID, token: str = Depends(oauth2_scheme)):
    """
    Endpoint para obtener el inventario total de un cliente.
    Requiere un token de autenticación.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        total_inventory = get_total_inventory_for_tenant(tenant_id)
        return {"total_inventory": total_inventory}
    except Exception as e:
        logging.error(f"Error in total inventory analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/sales_by_channel/{tenant_id}", status_code=status.HTTP_200_OK)
def get_sales_by_channel(tenant_id: UUID, token: str = Depends(oauth2_scheme)):
    """
    Endpoint para obtener las ventas por canal de un cliente.
    Requiere un token de autenticación.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        sales_by_channel = get_sales_by_channel_for_tenant(tenant_id)
        return {"sales_by_channel": sales_by_channel}
    except Exception as e:
        logging.error(f"Error in sales by channel analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/analytics/total_inventory_value/{tenant_id}", status_code=status.HTTP_200_OK)
def get_total_inventory_value(tenant_id: UUID, token: str = Depends(oauth2_scheme)):
    """
    Endpoint para obtener el valor total del inventario de un cliente.
    Requiere un token de autenticación.
    """
    payload = verify_token(token)
    if str(payload.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a estos datos."
        )

    try:
        total_value = get_total_inventory_value_for_tenant(tenant_id)
        return {"total_inventory_value": total_value}
    except Exception as e:
        logging.error(f"Error in total inventory value analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
