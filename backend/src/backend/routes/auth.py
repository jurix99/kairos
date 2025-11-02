"""
Routes API pour l'authentification OAuth
"""

import httpx
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..config.database import get_db
from ..services.auth_service import AuthService
from ..models.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


class GitHubUser(BaseModel):
    id: str
    name: str
    email: str
    picture: str
    provider: str


class GitHubAuthRequest(BaseModel):
    code: str
    state: str


@router.post("/github/callback", response_model=UserResponse)
async def github_callback(auth_request: GitHubAuthRequest, db: Session = Depends(get_db)):
    """
    Gérer le callback GitHub OAuth et échanger le code contre un token d'accès
    """
    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET
    
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500, 
            detail="GitHub OAuth credentials not configured"
        )
    
    try:
        # Échanger le code contre un token d'accès
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": auth_request.code,
                }
            )
            
            token_data = token_response.json()
            
            if "error" in token_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"GitHub token exchange failed: {token_data.get('error_description', token_data['error'])}"
                )
            
            access_token = token_data["access_token"]
            
            # Récupérer les informations de l'utilisateur
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/json",
                }
            )
            
            user_data = user_response.json()
            
            # Récupérer l'email principal
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/json",
                }
            )
            
            email_data = email_response.json()
            primary_email = None
            
            # Trouver l'email principal
            for email_info in email_data:
                if email_info.get("primary", False):
                    primary_email = email_info["email"]
                    break
            
            # Fallback sur l'email public si pas d'email principal trouvé
            if not primary_email:
                primary_email = user_data.get("email") or f"{user_data['login']}@github.local"
            
            # Créer ou récupérer l'utilisateur dans la base de données
            user_info = {
                "id": str(user_data["id"]),
                "name": user_data.get("name") or user_data["login"],
                "email": primary_email,
                "picture": user_data["avatar_url"],
                "provider": "github"
            }
            
            auth_service = AuthService(db)
            user = auth_service.get_or_create_user(user_info)
            
            return user
            
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with GitHub API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"GitHub authentication failed: {str(e)}"
        )


@router.get("/health")
async def auth_health():
    """Vérification de l'état du service d'authentification"""
    return {
        "status": "healthy",
        "github_configured": bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)
    } 