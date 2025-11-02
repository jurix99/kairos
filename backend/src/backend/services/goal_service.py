"""
Service de gestion des objectifs
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.database import Goal
from ..models.schemas import GoalCreate, GoalUpdate, GoalStatus, GoalCategory, PriorityLevel


class GoalService:
    """
    Service pour la gestion des objectifs
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_goals(
        self,
        user_id: int,
        status: Optional[GoalStatus] = None,
        category: Optional[GoalCategory] = None,
        priority: Optional[PriorityLevel] = None
    ) -> List[Goal]:
        """
        Récupère les objectifs avec filtres optionnels pour un utilisateur
        """
        query = self.db.query(Goal).filter(Goal.user_id == user_id)
        
        if status:
            query = query.filter(Goal.status == status)
        if category:
            query = query.filter(Goal.category == category)
        if priority:
            query = query.filter(Goal.priority == priority)
        
        return query.order_by(Goal.created_at.desc()).all()
    
    def get_goal_by_id(self, goal_id: int, user_id: int) -> Optional[Goal]:
        """
        Récupère un objectif par son ID pour un utilisateur spécifique
        """
        return self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).first()
    
    def create_goal(self, goal_data: GoalCreate, user_id: int) -> Goal:
        """
        Crée un nouvel objectif pour un utilisateur
        """
        goal = Goal(
            title=goal_data.title,
            description=goal_data.description,
            target_date=goal_data.target_date,
            priority=goal_data.priority,
            status=goal_data.status,
            category=goal_data.category,
            strategy=goal_data.strategy,
            success_criteria=goal_data.success_criteria,
            current_value=goal_data.current_value,
            target_value=goal_data.target_value,
            unit=goal_data.unit,
            user_id=user_id
        )
        
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def update_goal(self, goal_id: int, goal_data: GoalUpdate, user_id: int) -> Goal:
        """
        Met à jour un objectif pour un utilisateur
        """
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Objectif non trouvé")
        
        # Mettre à jour les champs modifiés
        update_data = goal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        
        # Si l'objectif passe à "completed", enregistrer la date de completion
        if goal_data.status == GoalStatus.COMPLETED and goal.completed_at is None:
            goal.completed_at = datetime.utcnow()
        elif goal_data.status != GoalStatus.COMPLETED:
            goal.completed_at = None
        
        goal.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(goal)
        return goal
    
    def delete_goal(self, goal_id: int, user_id: int) -> bool:
        """
        Supprime un objectif pour un utilisateur
        """
        goal = self.get_goal_by_id(goal_id, user_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Objectif non trouvé")
        
        self.db.delete(goal)
        self.db.commit()
        return True
    
    def get_goals_by_category(self, category: GoalCategory, user_id: int) -> List[Goal]:
        """
        Récupère tous les objectifs d'une catégorie pour un utilisateur
        """
        return self.db.query(Goal).filter(
            Goal.category == category,
            Goal.user_id == user_id
        ).all()
    
    def get_goals_by_status(self, status: GoalStatus, user_id: int) -> List[Goal]:
        """
        Récupère tous les objectifs d'un statut donné pour un utilisateur
        """
        return self.db.query(Goal).filter(
            Goal.status == status,
            Goal.user_id == user_id
        ).all()
    
    def get_goal_statistics(self, user_id: int) -> dict:
        """
        Récupère les statistiques des objectifs pour un utilisateur
        """
        total_goals = self.db.query(Goal).filter(Goal.user_id == user_id).count()
        active_goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.ACTIVE
        ).count()
        completed_goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.COMPLETED
        ).count()
        paused_goals = self.db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == GoalStatus.PAUSED
        ).count()
        
        # Statistiques par catégorie
        category_stats = {}
        for category in GoalCategory:
            count = self.db.query(Goal).filter(
                Goal.user_id == user_id,
                Goal.category == category
            ).count()
            if count > 0:
                category_stats[category.value] = count
        
        return {
            "total_goals": total_goals,
            "active_goals": active_goals,
            "completed_goals": completed_goals,
            "paused_goals": paused_goals,
            "completion_rate": completed_goals / total_goals * 100 if total_goals > 0 else 0,
            "category_distribution": category_stats
        }

