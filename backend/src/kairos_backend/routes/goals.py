"""
Routes API pour la gestion des objectifs
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..config.auth import get_current_user
from ..models.database import User
from ..models.schemas import GoalCreate, GoalUpdate, GoalResponse, GoalStatus, GoalCategory, PriorityLevel
from ..services.goal_service import GoalService

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/", response_model=List[GoalResponse])
async def get_goals(
    status: Optional[GoalStatus] = Query(None, description="Filtrer par statut"),
    category: Optional[GoalCategory] = Query(None, description="Filtrer par catégorie"),
    priority: Optional[PriorityLevel] = Query(None, description="Filtrer par priorité"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les objectifs avec filtres optionnels pour l'utilisateur connecté"""
    service = GoalService(db)
    return service.get_all_goals(current_user.id, status, category, priority)


@router.post("/", response_model=GoalResponse)
async def create_goal(
    goal: GoalCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un nouvel objectif"""
    service = GoalService(db)
    return service.create_goal(goal, current_user.id)


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer un objectif par son ID"""
    service = GoalService(db)
    goal = service.get_goal_by_id(goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Objectif non trouvé")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour un objectif"""
    service = GoalService(db)
    return service.update_goal(goal_id, goal_data, current_user.id)


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer un objectif"""
    service = GoalService(db)
    success = service.delete_goal(goal_id, current_user.id)
    return {"message": "Objectif supprimé avec succès"}


@router.get("/stats/overview")
async def get_goal_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les statistiques des objectifs pour l'utilisateur connecté"""
    service = GoalService(db)
    return service.get_goal_statistics(current_user.id)


@router.get("/category/{category}", response_model=List[GoalResponse])
async def get_goals_by_category(
    category: GoalCategory,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les objectifs d'une catégorie spécifique"""
    service = GoalService(db)
    return service.get_goals_by_category(category, current_user.id)


@router.get("/status/{status}", response_model=List[GoalResponse])
async def get_goals_by_status(
    status: GoalStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les objectifs d'un statut spécifique"""
    service = GoalService(db)
    return service.get_goals_by_status(status, current_user.id)

