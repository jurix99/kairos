"""
Configuration de la base de données SQLite
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .settings import settings


# Création du moteur SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Générateur de session de base de données pour l'injection de dépendance FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Créer toutes les tables de la base de données
    """
    from ..models.database import Base
    Base.metadata.create_all(bind=engine)


def init_default_categories(db: Session) -> None:
    """
    Initialiser les catégories par défaut
    """
    from ..models.database import Category
    
    default_categories = [
        {"name": "Travail", "color_code": "#3B82F6", "description": "Événements professionnels"},
        {"name": "Perso", "color_code": "#10B981", "description": "Événements personnels"},
        {"name": "Sport", "color_code": "#F59E0B", "description": "Activités sportives"},
        {"name": "Repos", "color_code": "#8B5CF6", "description": "Temps de repos et détente"},
    ]
    
    for cat_data in default_categories:
        # Vérifier si la catégorie existe déjà
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
    
    db.commit() 