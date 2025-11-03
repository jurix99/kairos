"""
Routes API pour la gestion des suggestions
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..config.auth import get_current_user
from ..models.schemas import (
    SuggestionResponse, 
    SuggestionUpdate,
    UserResponse
)
from ..services.rules_engine_service import RulesEngineService

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])


@router.get("/", response_model=List[SuggestionResponse])
def get_suggestions(
    status: Optional[str] = Query(None, description="Filtrer par statut (pending, accepted, rejected, expired)"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère toutes les suggestions actives pour l'utilisateur connecté
    """
    rules_service = RulesEngineService(db)
    
    if status == "pending" or status is None:
        # Récupérer les suggestions actives (non expirées)
        suggestions = rules_service.get_active_suggestions(current_user.id)
    else:
        # Récupérer toutes les suggestions avec le statut spécifié
        from ..models.database import Suggestion
        suggestions = db.query(Suggestion).filter(
            Suggestion.user_id == current_user.id,
            Suggestion.status == status
        ).order_by(
            Suggestion.created_at.desc()
        ).all()
    
    return suggestions


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
def get_suggestion(
    suggestion_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère une suggestion spécifique par son ID
    """
    rules_service = RulesEngineService(db)
    suggestion = rules_service.get_suggestion_by_id(suggestion_id, current_user.id)
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion non trouvée")
    
    return suggestion


@router.post("/generate", response_model=List[SuggestionResponse])
def generate_suggestions(
    date: Optional[datetime] = Query(None, description="Date pour laquelle générer les suggestions"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Génère de nouvelles suggestions pour l'utilisateur connecté à la date spécifiée
    """
    rules_service = RulesEngineService(db)
    suggestions = rules_service.generate_suggestions_for_user(
        current_user.id,
        date
    )
    
    return suggestions


@router.patch("/{suggestion_id}", response_model=SuggestionResponse)
def update_suggestion(
    suggestion_id: int,
    suggestion_update: SuggestionUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour le statut d'une suggestion (accepter, rejeter, etc.)
    """
    rules_service = RulesEngineService(db)
    
    suggestion = rules_service.update_suggestion_status(
        suggestion_id,
        current_user.id,
        suggestion_update.status
    )
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion non trouvée")
    
    return suggestion


@router.delete("/{suggestion_id}")
def delete_suggestion(
    suggestion_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprime une suggestion (marque comme rejetée)
    """
    rules_service = RulesEngineService(db)
    
    suggestion = rules_service.update_suggestion_status(
        suggestion_id,
        current_user.id,
        "rejected"
    )
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion non trouvée")
    
    return {"message": "Suggestion supprimée avec succès", "id": suggestion_id}

