"""
Routes API pour la gestion des catégories
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..config.auth import get_current_user, get_optional_current_user
from ..models.database import User
from ..models.schemas import CategoryCreate, CategoryResponse
from ..services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer toutes les catégories (par défaut + utilisateur si connecté)"""
    service = CategoryService(db)
    return service.get_all_categories(current_user.id if current_user else None)


@router.post("/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle catégorie"""
    service = CategoryService(db)
    return service.create_category(category)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Récupérer une catégorie par son ID"""
    service = CategoryService(db)
    category = service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int, 
    category_update: CategoryCreate, 
    db: Session = Depends(get_db)
):
    """Mettre à jour une catégorie"""
    service = CategoryService(db)
    return service.update_category(category_id, category_update)


@router.delete("/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Supprimer une catégorie"""
    service = CategoryService(db)
    service.delete_category(category_id)
    return {"message": "Catégorie supprimée avec succès"}


@router.get("/{category_id}/statistics")
async def get_category_statistics(category_id: int, db: Session = Depends(get_db)):
    """Récupérer les statistiques d'une catégorie"""
    service = CategoryService(db)
    return service.get_category_statistics(category_id) 