# app/database.py
#
# Archivo para manejar la conexión a la base de datos.
# Utiliza psycopg2 y el módulo dotenv para cargar la URL de la base de datos desde el archivo .env.

import os
import psycopg2
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env.
load_dotenv()

# Obtiene la URL de la base de datos desde las variables de entorno.
SUPABASE_URL = os.getenv("SUPABASE_URL")

def get_db_connection():
    """
    Establece una conexión con la base de datos PostgreSQL de Supabase.
    
    Raises:
        ValueError: Si la variable de entorno SUPABASE_URL no está configurada.
        
    Returns:
        psycopg2.extensions.connection: El objeto de conexión a la base de datos.
    """
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL no está configurada. Asegúrate de tener un archivo .env.")
    
    # Intenta establecer la conexión.
    conn = psycopg2.connect(SUPABASE_URL)
    return conn
