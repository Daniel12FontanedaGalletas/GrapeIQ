# main.py
#
# Este es el archivo principal de tu aplicación FastAPI.
# Aquí se configuran los routers y se definen los endpoints de la API.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sales, products, inventory, data, auth # ¡Nueva importación!
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Creamos la instancia principal de la aplicación FastAPI.
app = FastAPI(
    title="GrapeIQ API",
    description="API para la ingesta y consulta de datos de ventas, productos e inventario para GrapeIQ.",
    version="0.1.0",
)

# Configuración de CORS para permitir la conexión desde el dashboard en el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos los routers para cada dominio de negocio (ingesta, consulta y ahora, autenticación).
app.include_router(sales.router, prefix="/api/ingest/sales", tags=["sales"])
app.include_router(products.router, prefix="/api/ingest/products", tags=["products"])
app.include_router(inventory.router, prefix="/api/ingest/inventory", tags=["inventory"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"]) # ¡Nuevo router de autenticación!

@app.get("/")
def read_root():
    """
    Endpoint de bienvenida para la API.
    """
    return {"message": "Welcome to GrapeIQ API"}
