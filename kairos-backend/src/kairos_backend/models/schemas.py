"""
Schémas Pydantic pour la validation des données API
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PriorityLevel(str, Enum):
    """Niveaux de priorité pour les événements"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EventStatus(str, Enum):
    """Statuts possibles pour les événements"""
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Schémas pour les utilisateurs

class UserBase(BaseModel):
    """Schéma de base pour un utilisateur"""
    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., max_length=200)
    picture: Optional[str] = Field(None, max_length=500)
    provider: str = Field(..., max_length=50)


class UserCreate(UserBase):
    """Schéma pour créer un utilisateur"""
    external_id: str = Field(..., max_length=100)


class UserResponse(UserBase):
    """Schéma de réponse pour un utilisateur"""
    id: int
    external_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schémas pour les catégories

class CategoryBase(BaseModel):
    """Schéma de base pour une catégorie"""
    name: str = Field(..., min_length=1, max_length=50)
    color_code: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$")
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schéma pour créer une catégorie"""
    pass


class CategoryResponse(CategoryBase):
    """Schéma de réponse pour une catégorie"""
    id: int
    user_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# Schémas pour les événements

class EventBase(BaseModel):
    """Schéma de base pour un événement"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = Field(None, max_length=200)
    priority: PriorityLevel = PriorityLevel.MEDIUM
    status: EventStatus = EventStatus.PENDING
    is_flexible: bool = True
    category_id: int
    recurrence_rule: Optional[str] = Field(None, max_length=50)


class EventCreate(EventBase):
    """Schéma pour créer un événement"""
    pass


class EventUpdate(BaseModel):
    """Schéma pour mettre à jour un événement"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    priority: Optional[PriorityLevel] = None
    status: Optional[EventStatus] = None
    is_flexible: Optional[bool] = None
    category_id: Optional[int] = None
    recurrence_rule: Optional[str] = Field(None, max_length=50)


class EventResponse(EventBase):
    """Schéma de réponse pour un événement"""
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    category: CategoryResponse
    
    model_config = ConfigDict(from_attributes=True)


# Schémas pour le scheduling

class ConflictSuggestion(BaseModel):
    """Suggestion pour résoudre un conflit"""
    conflicting_event_id: int
    suggested_start_time: datetime
    reason: str


class SchedulingResult(BaseModel):
    """Résultat du scheduling automatique"""
    success: bool
    scheduled_time: Optional[datetime] = None
    conflicts: list[ConflictSuggestion] = []
    message: str 