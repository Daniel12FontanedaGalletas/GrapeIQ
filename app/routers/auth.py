# app/routers/auth.py
#
# Este archivo define los endpoints relacionados con la autenticación.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import create_access_token, mock_users
import logging

# Crea una instancia de APIRouter para los endpoints de autenticación.
router = APIRouter()

@router.post("/login", status_code=status.HTTP_200_OK)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para iniciar sesión y obtener un token de acceso.
    """
    user = mock_users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de usuario incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crea el token JWT que contiene el ID del cliente (`tenant_id`).
    access_token = create_access_token(
        data={"sub": user["username"], "tenant_id": user["tenant_id"]}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
