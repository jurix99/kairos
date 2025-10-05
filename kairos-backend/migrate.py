#!/usr/bin/env python3
"""
Script de migration pour initialiser la base de données Kairos
"""

import sys
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajouter le chemin source au PYTHONPATH
sys.path.insert(0, '/app/src')

from kairos_backend.config.settings import settings
from kairos_backend.models.database import Base, User, Category, Event


def create_tables():
    """Créer toutes les tables dans la base de données"""
    print(f"🗄️  Connexion à la base de données : {settings.DATABASE_URL}")
    
    # Créer l'engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Créer toutes les tables
    print("📋 Création des tables...")
    Base.metadata.create_all(bind=engine)
    
    # Vérifier si la colonne status existe, sinon l'ajouter
    from sqlalchemy import text
    try:
        with engine.connect() as connection:
            # Vérifier si la colonne status existe
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'events' AND column_name = 'status'
            """))
            
            if not result.fetchone():
                print("🔧 Ajout de la colonne 'status' à la table events...")
                connection.execute(text("ALTER TABLE events ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
                connection.commit()
                print("✅ Colonne 'status' ajoutée avec succès")
            
            # Vérifier si la colonne recurrence_rule existe
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'events' AND column_name = 'recurrence_rule'
            """))
            
            if not result.fetchone():
                print("🔧 Ajout de la colonne 'recurrence_rule' à la table events...")
                connection.execute(text("ALTER TABLE events ADD COLUMN recurrence_rule VARCHAR(50)"))
                connection.commit()
                print("✅ Colonne 'recurrence_rule' ajoutée avec succès")
            
            # Vérifier si la colonne parent_event_id existe
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'events' AND column_name = 'parent_event_id'
            """))
            
            if not result.fetchone():
                print("🔧 Ajout de la colonne 'parent_event_id' à la table events...")
                connection.execute(text("ALTER TABLE events ADD COLUMN parent_event_id INTEGER REFERENCES events(id)"))
                connection.commit()
                print("✅ Colonne 'parent_event_id' ajoutée avec succès")
                
    except Exception as e:
        print(f"⚠️  Avertissement lors de la vérification/ajout des colonnes : {e}")
    
    # Créer une session pour insérer des données par défaut
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Insérer des catégories par défaut si elles n'existent pas
        default_categories = [
            {"name": "Travail", "color_code": "#8B5CF6", "description": "Tâches professionnelles"},
            {"name": "Personnel", "color_code": "#06B6D4", "description": "Activités personnelles"},
            {"name": "Urgent", "color_code": "#EF4444", "description": "Tâches urgentes"},
            {"name": "Loisirs", "color_code": "#EC4899", "description": "Activités de détente"},
            {"name": "Santé", "color_code": "#F59E0B", "description": "Rendez-vous médicaux"},
        ]
        
        for cat_data in default_categories:
            existing = session.query(Category).filter(
                Category.name == cat_data["name"],
                Category.user_id.is_(None)
            ).first()
            
            if not existing:
                category = Category(
                    name=cat_data["name"],
                    color_code=cat_data["color_code"],
                    description=cat_data["description"],
                    user_id=None  # Catégorie globale
                )
                session.add(category)
        
        session.commit()
        print("✅ Tables créées avec succès !")
        print("📝 Catégories par défaut ajoutées")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de l'insertion des données par défaut : {e}")
    finally:
        session.close()


if __name__ == "__main__":
    create_tables() 