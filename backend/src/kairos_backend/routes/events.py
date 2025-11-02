"""
Routes API pour la gestion des événements
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..config.auth import get_current_user
from ..models.database import User
from ..models.schemas import EventCreate, EventUpdate, EventResponse, PriorityLevel
from ..services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=List[EventResponse])
async def get_events(
    start_date: Optional[datetime] = Query(None, description="Date de début pour filtrer"),
    end_date: Optional[datetime] = Query(None, description="Date de fin pour filtrer"),
    category_id: Optional[int] = Query(None, description="Filtrer par catégorie"),
    priority: Optional[PriorityLevel] = Query(None, description="Filtrer par priorité"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer les événements avec filtres optionnels pour l'utilisateur connecté"""
    service = EventService(db)
    return service.get_all_events(current_user.id, start_date, end_date, category_id, priority)


@router.post("/", response_model=EventResponse)
async def create_event(
    event: EventCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un nouvel événement pour l'utilisateur connecté"""
    service = EventService(db)
    return service.create_event(event, current_user.id)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupérer un événement par son ID pour l'utilisateur connecté"""
    service = EventService(db)
    event = service.get_event_by_id(event_id, current_user.id)
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    return event


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int, 
    event_update: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour un événement pour l'utilisateur connecté"""
    service = EventService(db)
    return service.update_event(event_id, event_update, current_user.id)


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer un événement pour l'utilisateur connecté"""
    service = EventService(db)
    service.delete_event(event_id, current_user.id)
    return {"message": "Événement supprimé avec succès"}


@router.get("/category/{category_id}", response_model=List[EventResponse])
async def get_events_by_category(category_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les événements d'une catégorie"""
    service = EventService(db)
    return service.get_events_by_category(category_id)


@router.get("/priority/{priority}", response_model=List[EventResponse])
async def get_events_by_priority(priority: PriorityLevel, db: Session = Depends(get_db)):
    """Récupérer tous les événements d'une priorité donnée"""
    service = EventService(db)
    return service.get_events_by_priority(priority)


@router.get("/flexible/list", response_model=List[EventResponse])
async def get_flexible_events(db: Session = Depends(get_db)):
    """Récupérer tous les événements flexibles"""
    service = EventService(db)
    return service.get_flexible_events()


@router.get("/statistics/overview")
async def get_event_statistics(db: Session = Depends(get_db)):
    """Récupérer les statistiques générales des événements"""
    service = EventService(db)
    return service.get_event_statistics() 