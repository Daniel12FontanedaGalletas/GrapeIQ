# app/services/auth.py
#
# Este archivo contiene la lógica de negocio para la autenticación y validación de tokens.
# En un entorno de producción, las credenciales del usuario se validarían contra una base de datos.

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from jose import jwt, JWTError
import logging
from uuid import UUID

# Clave secreta para firmar los tokens. ¡Debería ser una variable de entorno en producción!
SECRET_KEY = "super_secreta_e_insegura_clave"
ALGORITHM = "HS256"

# Esquema de autenticación. Indica que la API espera un token de portador.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Simulación de un usuario en un entorno de desarrollo.
# `tenant_id` es el UUID del cliente.
# En una aplicación real, esta información vendría de una base de datos.
mock_users = {
    "admin": {
        "username": "admin",
        "password": "password",
        "tenant_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    }
}

def create_access_token(data: dict):
    """
    Crea un token de acceso JWT con los datos proporcionados.
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verifica la validez de un token JWT y devuelve sus datos.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logging.error(f"Error validating JWT token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
