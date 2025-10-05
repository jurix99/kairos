"""
Configuration centralisée pour Kairos Backend
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Base de données
    DATABASE_URL: str = "postgresql://kairos_user:kairos_password@localhost:5432/kairos"
    
    # API
    API_TITLE: str = "Kairos - Agenda Intelligent"
    API_DESCRIPTION: str = "Backend pour un agenda intelligent avec scheduling automatique"
    API_VERSION: str = "0.1.0"
    
    # Serveur
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Scheduling
    DEFAULT_WORKING_HOURS_START: int = 8  # 8h
    DEFAULT_WORKING_HOURS_END: int = 20   # 20h
    DEFAULT_SEARCH_DAYS: int = 7
    SLOT_DURATION_MINUTES: int = 30
    
    # OAuth GitHub
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale des paramètres
settings = Settings() 