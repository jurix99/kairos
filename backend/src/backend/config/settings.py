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
    PORT: int = 8080
    DEBUG: bool = True
    
    # Scheduling
    DEFAULT_WORKING_HOURS_START: int = 8
    DEFAULT_WORKING_HOURS_END: int = 20
    DEFAULT_SEARCH_DAYS: int = 7
    SLOT_DURATION_MINUTES: int = 30
    
    # OAuth GitHub
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Travel Time API (optionnel)
    TRAVEL_API_PROVIDER: Optional[str] = None  # "google", "mapbox", "openroute"
    TRAVEL_API_KEY: Optional[str] = None
    USE_TRAVEL_API: bool = False  # Active l'utilisation de l'API pour les calculs de trajet
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale des paramètres
settings = Settings()