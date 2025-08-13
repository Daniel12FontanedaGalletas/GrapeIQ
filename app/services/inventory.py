# app/services/inventory.py
#
# Lógica de servicio para interactuar con la base de datos de inventario.
# Aquí se implementa la inserción de datos en la tabla 'inventory'.

from app.database import get_db_connection
from app.models.inventory import InventoryData
import logging

def ingest_inventory_data(inventory_data: InventoryData):
    """
    Ingiere datos de inventario en la tabla `inventory` de PostgreSQL.
    Utiliza un comando `UPSERT` para evitar duplicados.

    Args:
        inventory_data (InventoryData): El objeto de datos de inventario validado por Pydantic.
    """
    logging.info(f"Ingesting inventory data for tenant_id: {inventory_data.tenant_id}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Prepara un string con los valores a insertar.
        values = ', '.join([
            cur.mogrify(
                "(%s, %s, %s, %s, %s)",
                (
                    rec.date,
                    rec.sku,
                    rec.qty,
                    rec.location,
                    str(inventory_data.tenant_id)
                )
            ).decode('utf-8')
            for rec in inventory_data.data
        ])
        
        # Sentencia SQL para UPSERT.
        # Si la combinación (tenant_id, date, sku, location) ya existe, se actualiza la cantidad (qty).
        query = f"""
            INSERT INTO inventory (date, sku, qty, location, tenant_id)
            VALUES {values}
            ON CONFLICT (tenant_id, date, sku, location) DO UPDATE
            SET qty = EXCLUDED.qty;
        """
        
        cur.execute(query)
        conn.commit()
        logging.info(f"Successfully ingested {len(inventory_data.data)} inventory records.")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error during inventory data ingestion: {e}")
        raise e
        
    finally:
        cur.close()
        conn.close()
