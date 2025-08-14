# app/services/analytics.py
#
# Este archivo contiene la lógica de negocio para los cálculos analíticos.
# ¡MODIFICADO! para aceptar una conexión a la BD en lugar de crear una nueva.

import logging
from uuid import UUID
import psycopg2

def get_total_sales_for_tenant(conn: psycopg2.extensions.connection, tenant_id: UUID):
    """
    Calcula las ventas totales de un cliente (`tenant_id`).
    Usa la conexión a la base de datos proporcionada.
    """
    logging.info(f"Calculating total sales for tenant_id: {tenant_id}")
    
    try:
        # Usa 'with' para gestionar el cursor automáticamente
        with conn.cursor() as cur:
            # Consulta parametrizada para seguridad
            query = "SELECT SUM(qty * price) FROM sales WHERE tenant_id = %s;"
            cur.execute(query, (str(tenant_id),))
            total_sales = cur.fetchone()[0]
            
            return float(total_sales) if total_sales is not None else 0.0

    except Exception as e:
        logging.error(f"Error while calculating total sales: {e}")
        raise e

def get_total_inventory_for_tenant(conn: psycopg2.extensions.connection, tenant_id: UUID):
    """
    Calcula el total de unidades de inventario de un cliente (`tenant_id`).
    """
    logging.info(f"Calculating total inventory for tenant_id: {tenant_id}")
    
    try:
        with conn.cursor() as cur:
            query = "SELECT SUM(qty) FROM inventory WHERE tenant_id = %s;"
            cur.execute(query, (str(tenant_id),))
            total_inventory = cur.fetchone()[0]
            
            return int(total_inventory) if total_inventory is not None else 0

    except Exception as e:
        logging.error(f"Error while calculating total inventory: {e}")
        raise e

def get_sales_by_channel_for_tenant(conn: psycopg2.extensions.connection, tenant_id: UUID):
    """
    Calcula las ventas totales agrupadas por canal (ubicación) para un cliente.
    """
    logging.info(f"Calculating sales by channel for tenant_id: {tenant_id}")

    try:
        with conn.cursor() as cur:
            query = """
                SELECT i.location, SUM(s.qty * s.price)
                FROM sales s
                JOIN inventory i ON s.sku = i.sku AND s.tenant_id = i.tenant_id
                WHERE s.tenant_id = %s
                GROUP BY i.location;
            """
            cur.execute(query, (str(tenant_id),))
            results = cur.fetchall()

            sales_by_channel = {
                location: float(total_sales) if total_sales is not None else 0.0
                for location, total_sales in results
            }
            
            return sales_by_channel

    except Exception as e:
        logging.error(f"Error while calculating sales by channel: {e}")
        raise e
        
def get_total_inventory_value_for_tenant(conn: psycopg2.extensions.connection, tenant_id: UUID):
    """
    Calcula el valor monetario total del inventario para un cliente.
    """
    logging.info(f"Calculating total inventory value for tenant_id: {tenant_id}")

    try:
        with conn.cursor() as cur:
            query = """
                SELECT SUM(i.qty * p.price)
                FROM inventory i
                JOIN products p ON i.sku = p.sku AND i.tenant_id = p.tenant_id
                WHERE i.tenant_id = %s;
            """
            cur.execute(query, (str(tenant_id),))
            total_value = cur.fetchone()[0]

            return float(total_value) if total_value is not None else 0.0

    except Exception as e:
        logging.error(f"Error while calculating total inventory value: {e}")
        raise e