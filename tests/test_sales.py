# tests/test_sales.py
#
# Tests mínimos para el endpoint de ingesta de ventas usando pytest.
# Mockeamos la conexión a la base de datos para no depender de una conexión real.

import os
import sys
# Añade el directorio raíz del proyecto al sys.path para que los módulos puedan ser encontrados.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from main import app
from datetime import date
import uuid

# Creamos una instancia de TestClient de FastAPI para simular peticiones HTTP.
client = TestClient(app)

# Nota: El fixture 'mock_db_connection' no se necesita con este enfoque.
# La función 'test_ingest_sales_success' se modificará para usar un patch directo.

def test_ingest_sales_success():
    """
    Prueba que el endpoint de ingesta de ventas funcione correctamente con datos válidos.
    Ahora usamos un patch para simular la conexión a la base de datos.
    """
    with patch('app.services.sales.get_db_connection') as mock_get_conn:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.mogrify.side_effect = lambda sql, params: (sql % params).encode('utf-8')

        tenant_id = uuid.uuid4()
        sales_data = {
            "tenant_id": str(tenant_id),
            "data": [
                {"date": "2024-01-01", "sku": "VINO-001", "qty": 10, "price": 15.5, "channel": "online"},
                {"date": "2024-01-02", "sku": "VINO-002", "qty": 5, "price": 20.0, "channel": "tienda"},
            ]
        }
        
        response = client.post("/api/ingest/sales", json=sales_data)
        
        assert response.status_code == 201
        assert response.json() == {"message": "Sales data ingested successfully."}
        
        # Verificamos que los métodos del mock se hayan llamado correctamente.
        mock_get_conn.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
    
def test_ingest_sales_invalid_data():
    """
    Prueba que el endpoint maneje datos inválidos (ej. fecha incorrecta) y retorne un error 422.
    """
    tenant_id = uuid.uuid4()
    sales_data_invalid = {
        "tenant_id": str(tenant_id),
        "data": [
            {"date": "not-a-date", "sku": "VINO-001", "qty": 10, "price": 15.5, "channel": "online"},
        ]
    }
    
    response = client.post("/api/ingest/sales", json=sales_data_invalid)
    
    assert response.status_code == 422