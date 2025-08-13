# app/services/analytics.py
#
# Este archivo contiene la lógica de negocio para los cálculos analíticos.

from app.database import get_db_connection
import logging
from uuid import UUID

def get_total_sales_for_tenant(tenant_id: UUID):
    """
    Calcula las ventas totales de un cliente (`tenant_id`).
    """
    logging.info(f"Calculating total sales for tenant_id: {tenant_id}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Consulta SQL para sumar (qty * price) y obtener el total de ventas.
        query = f"SELECT SUM(qty * price) FROM sales WHERE tenant_id = '{tenant_id}';"
        cur.execute(query)
        total_sales = cur.fetchone()[0] # Obtiene el primer resultado de la consulta.
        
        # Si no hay ventas, devuelve 0.
        return float(total_sales) if total_sales is not None else 0.0

    except Exception as e:
        logging.error(f"Error while calculating total sales: {e}")
        raise e
        
    finally:
        cur.close()
        conn.close()

def get_total_inventory_for_tenant(tenant_id: UUID):
    """
    Calcula el total de unidades de inventario de un cliente (`tenant_id`).
    """
    logging.info(f"Calculating total inventory for tenant_id: {tenant_id}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Consulta SQL para sumar la cantidad (`qty`) de todos los registros de inventario.
        query = f"SELECT SUM(qty) FROM inventory WHERE tenant_id = '{tenant_id}';"
        cur.execute(query)
        total_inventory = cur.fetchone()[0] # Obtiene el primer resultado de la consulta.
        
        # Si no hay inventario, devuelve 0.
        return int(total_inventory) if total_inventory is not None else 0

    except Exception as e:
        logging.error(f"Error while calculating total inventory: {e}")
        raise e
        
    finally:
        cur.close()
        conn.close()

def get_sales_by_channel_for_tenant(tenant_id: UUID):
    """
    Calcula las ventas totales agrupadas por canal (ubicación) para un cliente.
    """
    logging.info(f"Calculating sales by channel for tenant_id: {tenant_id}")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Usamos un JOIN para conectar los registros de ventas con el inventario
        # y así obtener la ubicación (`location`).
        # Luego agrupamos por ubicación y sumamos las ventas.
        query = f"""
            SELECT i.location, SUM(s.qty * s.price)
            FROM sales s
            JOIN inventory i ON s.sku = i.sku AND s.tenant_id = i.tenant_id
            WHERE s.tenant_id = '{tenant_id}'
            GROUP BY i.location;
        """
        cur.execute(query)
        results = cur.fetchall()

        # Convierte los resultados en un diccionario para un acceso más fácil
        sales_by_channel = {
            location: float(total_sales) if total_sales is not None else 0.0
            for location, total_sales in results
        }
        
        return sales_by_channel

    except Exception as e:
        logging.error(f"Error while calculating sales by channel: {e}")
        raise e

    finally:
        cur.close()
        conn.close()
        
def get_total_inventory_value_for_tenant(tenant_id: UUID):
    """
    Calcula el valor monetario total del inventario para un cliente.
    """
    logging.info(f"Calculating total inventory value for tenant_id: {tenant_id}")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Usamos un JOIN para combinar la cantidad de inventario con el precio del producto.
        # Luego sumamos la multiplicación (qty * price) para obtener el valor total.
        query = f"""
            SELECT SUM(i.qty * p.price)
            FROM inventory i
            JOIN products p ON i.sku = p.sku AND i.tenant_id = p.tenant_id
            WHERE i.tenant_id = '{tenant_id}';
        """
        cur.execute(query)
        total_value = cur.fetchone()[0]

        return float(total_value) if total_value is not None else 0.0

    except Exception as e:
        logging.error(f"Error while calculating total inventory value: {e}")
        raise e

    finally:
        cur.close()
        conn.close()