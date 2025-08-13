# app/services/products.py
#
# Lógica de servicio para interactuar con la base de datos de productos.
# Aquí se implementa la inserción de datos en la tabla 'products'.

from app.database import get_db_connection
from app.models.products import ProductsData
import logging

def ingest_products_data(products_data: ProductsData):
    """
    Ingiere datos de productos en la tabla `products` de PostgreSQL.
    Utiliza un comando `UPSERT` para evitar duplicados.

    Args:
        products_data (ProductsData): El objeto de datos de productos validado por Pydantic.
    """
    logging.info(f"Ingesting products data for tenant_id: {products_data.tenant_id}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Prepara un string con los valores a insertar.
        values = ', '.join([
            cur.mogrify(
                "(%s, %s, %s, %s, %s, %s)",
                (
                    rec.sku,
                    rec.name,
                    rec.category,
                    rec.price,
                    rec.description,
                    str(products_data.tenant_id)
                )
            ).decode('utf-8')
            for rec in products_data.data
        ])
        
        # Sentencia SQL para UPSERT.
        # Si la combinación (tenant_id, sku) ya existe, se actualizan los otros campos.
        query = f"""
            INSERT INTO products (sku, name, category, price, description, tenant_id)
            VALUES {values}
            ON CONFLICT (tenant_id, sku) DO UPDATE
            SET name = EXCLUDED.name, category = EXCLUDED.category, price = EXCLUDED.price, description = EXCLUDED.description;
        """
        
        cur.execute(query)
        conn.commit()
        logging.info(f"Successfully ingested {len(products_data.data)} product records.")
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Error during products data ingestion: {e}")
        raise e
        
    finally:
        cur.close()
        conn.close()