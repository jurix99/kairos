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
    print(f"🔍 Authorization header: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization:
        print("❌ No authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )    
    try:
        # Le token est envoyé sous forme de JSON encodé
        if not authorization.startswith("Bearer "):
            print(f"❌ Invalid format, doesn't start with Bearer")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        token = authorization.replace("Bearer ", "")
        print(f"✅ Token extracted: {token[:100]}...")
        user_data = json.loads(token)
        print(f"✅ JSON parsed successfully: {user_data.keys()}")
        
        auth_service = AuthService(db)
        print(f"🔍 Validating token with user_data: id={user_data.get('id') or user_data.get('external_id')}, provider={user_data.get('provider')}")
        user = auth_service.validate_user_token(user_data)
        print(f"✅ User validated: {user.email}")
        
        return user
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Token received: {authorization[:100]}...")  # Print first 100 chars
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Authentication error: {type(e).__name__}: {str(e)}")
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