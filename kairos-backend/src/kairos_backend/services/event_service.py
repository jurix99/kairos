"""
Service de gestion des événements
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from ..models.database import Event, Category
from ..models.schemas import EventCreate, EventUpdate, PriorityLevel


class EventService:
    """
    Service pour la gestion des événements
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_events(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_id: Optional[int] = None,
        priority: Optional[PriorityLevel] = None
    ) -> List[Event]:
        """
        Récupère les événements avec filtres optionnels pour un utilisateur
        """
        query = self.db.query(Event).options(joinedload(Event.category)).filter(Event.user_id == user_id)
        
        if start_date:
            query = query.filter(Event.start_time >= start_date)
        if end_date:
            query = query.filter(Event.end_time <= end_date)
        if category_id:
            query = query.filter(Event.category_id == category_id)
        if priority:
            query = query.filter(Event.priority == priority)
        
        return query.order_by(Event.start_time).all()
    
    def get_event_by_id(self, event_id: int, user_id: int) -> Optional[Event]:
        """
        Récupère un événement par son ID pour un utilisateur spécifique
        """
        return self.db.query(Event).options(joinedload(Event.category)).filter(
            Event.id == event_id,
            Event.user_id == user_id
        ).first()
    
    def create_event(self, event_data: EventCreate, user_id: int) -> Event:
        """
        Crée un nouvel événement pour un utilisateur
        """
        # Vérifier que la catégorie existe
        category = self.db.query(Category).filter(Category.id == event_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        
        # S'assurer que start_time est avant end_time
        if event_data.start_time >= event_data.end_time:
            raise HTTPException(status_code=400, detail="L'heure de début doit être avant l'heure de fin")
        
        # Créer l'événement
        db_event = Event(
            title=event_data.title,
            description=event_data.description,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            location=event_data.location,
            priority=event_data.priority,
            status=event_data.status,
            is_flexible=event_data.is_flexible,
            category_id=event_data.category_id,
            user_id=user_id,
            recurrence_rule=event_data.recurrence_rule
        )
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def update_event(self, event_id: int, event_data: EventUpdate, user_id: int) -> Event:
        """
        Met à jour un événement existant pour un utilisateur
        """
        event = self.get_event_by_id(event_id, user_id)
        if not event:
            raise HTTPException(status_code=404, detail="Événement non trouvé")
        
        # Mettre à jour les champs modifiés
        update_data = event_data.model_dump(exclude_unset=True)
        
        # S'assurer que start_time est avant end_time si les deux sont fournis
        start_time = update_data.get("start_time", event.start_time)
        end_time = update_data.get("end_time", event.end_time)
        if start_time >= end_time:
            raise HTTPException(status_code=400, detail="L'heure de début doit être avant l'heure de fin")

        # Vérifier la catégorie si elle est modifiée
        if "category_id" in update_data:
            category = self.db.query(Category).filter(Category.id == update_data["category_id"]).first()
            if not category:
                raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        
        for field, value in update_data.items():
            setattr(event, field, value)
        
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def delete_event(self, event_id: int, user_id: int) -> bool:
        """
        Supprime un événement pour un utilisateur
        """
        event = self.get_event_by_id(event_id, user_id)
        if not event:
            raise HTTPException(status_code=404, detail="Événement non trouvé")
        
        self.db.delete(event)
        self.db.commit()
        return True
    
    def get_events_by_category(self, category_id: int) -> List[Event]:
        """
        Récupère tous les événements d'une catégorie
        """
        return self.db.query(Event).filter(Event.category_id == category_id).all()
    
    def get_events_by_priority(self, priority: PriorityLevel) -> List[Event]:
        """
        Récupère tous les événements d'une priorité donnée
        """
        return self.db.query(Event).filter(Event.priority == priority).all()
    
    def get_flexible_events(self) -> List[Event]:
        """
        Récupère tous les événements flexibles
        """
        return self.db.query(Event).filter(Event.is_flexible == True).all()
    
    def get_events_in_timerange(self, start_time: datetime, end_time: datetime) -> List[Event]:
        """
        Récupère les événements dans une plage horaire donnée
        """
        return self.db.query(Event).filter(
            Event.start_time < end_time,
            Event.end_time > start_time
        ).all()
    
    def get_event_statistics(self) -> dict:
        """
        Récupère les statistiques générales des événements
        """
        total_events = self.db.query(Event).count()
        flexible_events = self.db.query(Event).filter(Event.is_flexible == True).count()
        
        # Statistiques par priorité
        high_priority = self.db.query(Event).filter(Event.priority == PriorityLevel.HIGH).count()
        medium_priority = self.db.query(Event).filter(Event.priority == PriorityLevel.MEDIUM).count()
        low_priority = self.db.query(Event).filter(Event.priority == PriorityLevel.LOW).count()
        
        return {
            "total_events": total_events,
            "flexible_events": flexible_events,
            "fixed_events": total_events - flexible_events,
            "priority_distribution": {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority
            }
        } 