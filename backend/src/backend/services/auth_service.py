"""
Service de gestion de l'authentification et des utilisateurs
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.database import User
from ..models.schemas import UserCreate, UserResponse


class AuthService:
    """
    Service pour la gestion de l'authentification et des utilisateurs
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, user_data: dict) -> User:
        """
        Récupère un utilisateur existant ou le crée s'il n'existe pas
        """
        # Chercher l'utilisateur par external_id et provider
        existing_user = self.db.query(User).filter(
            User.external_id == user_data["id"],
            User.provider == user_data["provider"]
        ).first()
        
        if existing_user:
            # Mettre à jour les informations de l'utilisateur
            existing_user.name = user_data["name"]
            existing_user.email = user_data["email"]
            existing_user.picture = user_data.get("picture")
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user
        
        # Créer un nouvel utilisateur
        new_user = User(
            external_id=user_data["id"],
            name=user_data["name"],
            email=user_data["email"],
            picture=user_data.get("picture"),
            provider=user_data["provider"]
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par son ID
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_external_id(self, external_id: str, provider: str) -> Optional[User]:
        """
        Récupère un utilisateur par son ID externe et provider
        """
        return self.db.query(User).filter(
            User.external_id == external_id,
            User.provider == provider
        ).first()
    
    def validate_user_token(self, token_data: dict) -> User:
        """
        Valide un token utilisateur et retourne l'utilisateur
        """
        if not token_data or "id" not in token_data or "provider" not in token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        user = self.get_user_by_external_id(
            token_data["id"], 
            token_data["provider"]
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user 