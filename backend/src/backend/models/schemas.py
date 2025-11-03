"""
Schémas Pydantic pour la validation des données API
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, validator


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


class GoalStatus(str, Enum):
    """Statuts possibles pour les objectifs"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class GoalCategory(str, Enum):
    """Catégories d'objectifs"""
    SPORT = "sport"
    CAREER = "career"
    HEALTH = "health"
    EDUCATION = "education"
    PERSONAL = "personal"
    FINANCIAL = "financial"
    RELATIONSHIPS = "relationships"
    HOBBIES = "hobbies"
    OTHER = "other"


class RecurrenceType(str, Enum):
    """Types de récurrence"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class RecurrenceRule(BaseModel):
    """Règle de récurrence pour un événement"""
    type: RecurrenceType
    interval: int = Field(default=1, ge=1, le=365)  # Tous les X jours/semaines/mois/années
    days_of_week: Optional[List[int]] = Field(None, description="Jours de la semaine (0=Lundi, 6=Dimanche)")
    end_date: Optional[datetime] = Field(None, description="Date de fin de récurrence")
    count: Optional[int] = Field(None, ge=1, le=1000, description="Nombre d'occurrences")
    
    @validator('days_of_week')
    def validate_days_of_week(cls, v):
        if v is not None:
            if not all(0 <= day <= 6 for day in v):
                raise ValueError('Days of week must be between 0 (Monday) and 6 (Sunday)')
            if len(set(v)) != len(v):
                raise ValueError('Days of week must be unique')
        return v
    
    @validator('count')
    def validate_end_condition(cls, v, values):
        if v is not None and values.get('end_date') is not None:
            raise ValueError('Cannot specify both end_date and count')
        return v


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
    recurrence: Optional[RecurrenceRule] = None


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
    recurrence: Optional[RecurrenceRule] = None


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


# Schémas pour les objectifs

class GoalBase(BaseModel):
    """Schéma de base pour un objectif"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    status: GoalStatus = GoalStatus.ACTIVE
    category: Optional[GoalCategory] = None
    strategy: Optional[str] = None
    success_criteria: Optional[str] = None
    current_value: Optional[str] = Field(None, max_length=100)
    target_value: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)


class GoalCreate(GoalBase):
    """Schéma pour créer un objectif"""
    pass


class GoalUpdate(BaseModel):
    """Schéma pour mettre à jour un objectif"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[GoalStatus] = None
    category: Optional[GoalCategory] = None
    strategy: Optional[str] = None
    success_criteria: Optional[str] = None
    current_value: Optional[str] = Field(None, max_length=100)
    target_value: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)


class GoalResponse(GoalBase):
    """Schéma de réponse pour un objectif"""
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)


# Schémas pour les suggestions

class SuggestionType(str, Enum):
    """Types de suggestions"""
    TAKE_BREAK = "take_break"
    BALANCE_DAY = "balance_day"
    MOVE_EVENT = "move_event"


class SuggestionStatus(str, Enum):
    """Statuts possibles pour les suggestions"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class SuggestionBase(BaseModel):
    """Schéma de base pour une suggestion"""
    type: SuggestionType
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    priority: PriorityLevel = PriorityLevel.MEDIUM
    status: SuggestionStatus = SuggestionStatus.PENDING
    extra_data: Optional[str] = None  # JSON string
    rule_triggered: str = Field(..., max_length=100)
    expires_at: Optional[datetime] = None
    related_event_id: Optional[int] = None


class SuggestionCreate(SuggestionBase):
    """Schéma pour créer une suggestion"""
    pass


class SuggestionUpdate(BaseModel):
    """Schéma pour mettre à jour une suggestion"""
    status: Optional[SuggestionStatus] = None


class SuggestionResponse(SuggestionBase):
    """Schéma de réponse pour une suggestion"""
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    
    model_config = ConfigDict(from_attributes=True) 