# app/database.py

import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import logging

# Carga las variables de entorno.
load_dotenv()

# Variable global para almacenar el pool de conexiones.
# Se inicializará al arrancar la aplicación.
db_pool = None

def init_db_pool():
    """Inicializa el pool de conexiones a la base de datos."""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10, # Puedes ajustar este número según la carga esperada
            dsn=os.getenv("SUPABASE_URL")
        )
        logging.info("Pool de conexiones a la base de datos inicializado con éxito.")
    except psycopg2.OperationalError as e:
        logging.error(f"No se pudo conectar a la base de datos: {e}")
        db_pool = None

def close_db_pool():
    """Cierra todas las conexiones en el pool."""
    global db_pool
    if db_pool:
        db_pool.closeall()
        logging.info("Pool de conexiones cerrado.")

def get_db_connection():
    """
    Obtiene una conexión del pool.
    Esta función será usada como una dependencia de FastAPI.
    """
    if not db_pool:
        raise HTTPException(status_code=503, detail="El servicio de base de datos no está disponible.")
    
    conn = None
    try:
        conn = db_pool.getconn()
        yield conn
    finally:
        if conn:
            db_pool.putconn(conn)