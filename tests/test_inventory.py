# tests/test_inventory.py
#
# Tests para el endpoint de ingesta de inventario.
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

def test_ingest_inventory_success():
    """
    Prueba que el endpoint de ingesta de inventario funcione correctamente con datos válidos.
    El test mockea la conexión a la base de datos para evitar llamadas reales.
    """
    with patch('app.services.inventory.get_db_connection') as mock_get_conn:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Simula el comportamiento de mogrify, que se usa para escapar los valores.
        mock_cursor.mogrify.side_effect = lambda sql, params: (sql % params).encode('utf-8')
        
        tenant_id = uuid.uuid4()
        inventory_data = {
            "tenant_id": str(tenant_id),
            "data": [
                {"date": "2024-01-01", "sku": "VINO-001", "qty": 100, "location": "almacen_a"},
                {"date": "2024-01-01", "sku": "VINO-002", "qty": 50, "location": "almacen_b"},
            ]
        }
        
        response = client.post("/api/ingest/inventory/", json=inventory_data)
        
        # Verificamos que la respuesta sea un código 201 (Created).
        assert response.status_code == 201
        assert response.json() == {"message": "Inventory data ingested successfully."}
        
        # Verificamos que los métodos del mock se hayan llamado.
        mock_get_conn.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

def test_ingest_inventory_invalid_data():
    """
    Prueba que el endpoint maneje datos inválidos (ej. fecha incorrecta) y retorne un error 422.
    """
    tenant_id = uuid.uuid4()
    inventory_data_invalid = {
        "tenant_id": str(tenant_id),
        "data": [
            {"date": "not-a-date", "sku": "VINO-001", "qty": 100, "location": "almacen_a"},
        ]
    }
    
    response = client.post("/api/ingest/inventory/", json=inventory_data_invalid)
    
    # Verificamos que el código de estado sea 422 (Unprocessable Entity).
    assert response.status_code == 422