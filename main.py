# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import sales, products, inventory, data, auth, forecast, results
from app.database import init_db_pool, close_db_pool
from contextlib import asynccontextmanager
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Gestor del ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta al iniciar la aplicación
    init_db_pool()
    yield
    # Código que se ejecuta al detener la aplicación
    close_db_pool()

# Creamos la instancia principal de la aplicación con el gestor de ciclo de vida
app = FastAPI(
    title="GrapeIQ API",
    description="API para la ingesta y consulta de datos de ventas, productos e inventario para GrapeIQ.",
    version="0.1.0",
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluimos los routers
app.include_router(sales.router, prefix="/api/ingest/sales", tags=["sales"])
app.include_router(products.router, prefix="/api/ingest/products", tags=["products"])
app.include_router(inventory.router, prefix="/api/ingest/inventory", tags=["inventory"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["forecast"])
app.include_router(results.router, prefix="/api/forecast", tags=["forecast"])

@app.get("/")
def read_root():
    """Endpoint de bienvenida para la API."""
    return {"message": "Welcome to GrapeIQ API"}