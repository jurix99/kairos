"""
Service de gestion des catégories
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.database import Category, Event
from ..models.schemas import CategoryCreate, CategoryResponse


class CategoryService:
    """
    Service pour la gestion des catégories
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_categories(self, user_id: Optional[int] = None) -> List[Category]:
        """
        Récupère toutes les catégories (par défaut + utilisateur si spécifié)
        """
        query = self.db.query(Category)
        
        if user_id:
            # Récupérer les catégories par défaut (user_id is null) ET celles de l'utilisateur
            query = query.filter((Category.user_id == user_id) | (Category.user_id.is_(None)))
        else:
            # Seulement les catégories par défaut si pas d'utilisateur
            query = query.filter(Category.user_id.is_(None))
        
        return query.all()
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """
        Récupère une catégorie par son ID
        """
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """
        Récupère une catégorie par son nom
        """
        return self.db.query(Category).filter(Category.name == name).first()
    
    def create_category(self, category_data: CategoryCreate) -> Category:
        """
        Crée une nouvelle catégorie
        """
        # Vérifier si le nom existe déjà
        existing = self.get_category_by_name(category_data.name)
        if existing:
            raise HTTPException(
                status_code=400, 
                detail="Une catégorie avec ce nom existe déjà"
            )
        
        db_category = Category(**category_data.model_dump())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def update_category(self, category_id: int, category_data: CategoryCreate) -> Category:
        """
        Met à jour une catégorie existante
        """
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        
        # Vérifier si le nouveau nom existe déjà (sauf pour la catégorie actuelle)
        if category_data.name != category.name:
            existing = self.get_category_by_name(category_data.name)
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail="Une catégorie avec ce nom existe déjà"
                )
        
        for field, value in category_data.model_dump().items():
            setattr(category, field, value)
        
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """
        Supprime une catégorie
        """
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        
        # Vérifier s'il y a des événements associés
        events_count = self.db.query(Event).filter(Event.category_id == category_id).count()
        if events_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Impossible de supprimer la catégorie: {events_count} événement(s) associé(s)"
            )
        
        self.db.delete(category)
        self.db.commit()
        return True
    
    def get_category_statistics(self, category_id: int) -> dict:
        """
        Récupère les statistiques d'une catégorie
        """
        category = self.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        
        events_count = self.db.query(Event).filter(Event.category_id == category_id).count()
        
        return {
            "category_id": category_id,
            "category_name": category.name,
            "total_events": events_count,
            "color_code": category.color_code
        } 