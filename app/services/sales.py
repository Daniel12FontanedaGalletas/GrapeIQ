# app/services/sales.py
#
# Lógica de servicio para interactuar con la base de datos de ventas.
# Aquí se implementa la inserción de datos en la tabla 'sales'.

from app.database import get_db_connection
from app.models.sales import SalesData
import logging

def ingest_sales_data(sales_data: SalesData):
    """
    Ingiere datos de ventas en la tabla `sales` de PostgreSQL.
    Utiliza un comando `UPSERT` para evitar duplicados en caso de que los datos ya existan.

    Args:
        sales_data (SalesData): El objeto de datos de ventas validado por Pydantic.
    """
    logging.info(f"Ingesting sales data for tenant_id: {sales_data.tenant_id}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Prepara un string con los valores a insertar. Esto es más eficiente
        # que realizar una inserción por cada registro.
        values = ', '.join([
            cur.mogrify(
                "(%s, %s, %s, %s, %s, %s)",
                (
                    rec.date,
                    rec.sku,
                    rec.qty,
                    rec.price,
                    rec.channel,
                    # Convertimos el UUID a string para que psycopg2 lo pueda manejar.
                    str(sales_data.tenant_id)
                )
            ).decode('utf-8')
            for rec in sales_data.data
        ])
        
        # Sentencia SQL para UPSERT (INSERT ... ON CONFLICT DO UPDATE).
        # Si la combinación (tenant_id, date, sku) ya existe,
        # se actualizan la cantidad y el precio.
        query = f"""
            INSERT INTO sales (date, sku, qty, price, channel, tenant_id)
            VALUES {values}
            ON CONFLICT (tenant_id, date, sku) DO UPDATE
            SET qty = EXCLUDED.qty, price = EXCLUDED.price;
        """
        
        cur.execute(query)
        conn.commit()
        logging.info(f"Successfully ingested {len(sales_data.data)} sales records.")
        
    except Exception as e:
        # Si hay un error, se deshace la transacción.
        conn.rollback()
        logging.error(f"Error during sales data ingestion: {e}")
        # Relanzamos la excepción para que sea manejada por el router.
        raise e
        
    finally:
        # Aseguramos que la conexión se cierre correctamente.
        cur.close()
        conn.close()
