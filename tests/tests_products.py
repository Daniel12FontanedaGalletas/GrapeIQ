# tests/test_products.py
#
# Tests para el endpoint de ingesta de productos.
# Mockeamos la conexión a la base de datos para pruebas unitarias.

import os
import sys
# Añade el directorio raíz del proyecto al sys.path para que los módulos puedan ser encontrados.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from main import app
import uuid

# Creamos una instancia de TestClient para simular peticiones HTTP a la aplicación.
client = TestClient(app)

def test_ingest_products_success():
    """
    Prueba que el endpoint de ingesta de productos funcione correctamente con datos válidos.
    El test mockea la conexión a la base de datos para evitar llamadas reales.
    """
    with patch('app.services.products.get_db_connection') as mock_get_conn:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simula el comportamiento de mogrify, que se usa para escapar los valores.
        mock_cursor.mogrify.side_effect = lambda sql, params: (sql % params).encode('utf-8')
        
        tenant_id = uuid.uuid4()
        products_data = {
            "tenant_id": str(tenant_id),
            "data": [
                {"sku": "VINO-001", "name": "Vino Tinto Gran Reserva", "category": "Vino Tinto", "price": 15.50},
                {"sku": "VINO-002", "name": "Vino Blanco Joven", "category": "Vino Blanco", "price": 12.00},
            ]
        }
        
        response = client.post("/api/ingest/products", json=products_data)
        
        # Verificamos que la respuesta sea un código 201 (Created).
        assert response.status_code == 201
        assert response.json() == {"message": "Products data ingested successfully."}
        
        # Verificamos que los métodos del mock se hayan llamado.
        mock_get_conn.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

def test_ingest_products_invalid_data():
    """
    Prueba que el endpoint maneje datos inválidos (ej. precio negativo) y retorne un error 422.
    """
    tenant_id = uuid.uuid4()
    products_data_invalid = {
        "tenant_id": str(tenant_id),
        "data": [
            {"sku": "VINO-001", "name": "Vino Tinto Gran Reserva", "category": "Vino Tinto", "price": -10.0},
        ]
    }
    
    response = client.post("/api/ingest/products", json=products_data_invalid)
    
    # Verificamos que el código de estado sea 422 (Unprocessable Entity).
    assert response.status_code == 422