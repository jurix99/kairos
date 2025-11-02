"""
Configuration et dépendances d'authentification
"""

import json
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from .database import get_db
from ..models.database import User
from ..services.auth_service import AuthService


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dépendance FastAPI pour récupérer l'utilisateur actuel
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        # Le token est envoyé sous forme de JSON encodé
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        token = authorization.replace("Bearer ", "")
        user_data = json.loads(token)
        
        auth_service = AuthService(db)
        user = auth_service.validate_user_token(user_data)
        
        return user
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dépendance FastAPI pour récupérer l'utilisateur actuel (optionnel)
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None 