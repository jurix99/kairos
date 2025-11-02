"""
Service de gestion des événements
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from ..models.database import Event, Category
from ..models.schemas import EventCreate, EventUpdate, PriorityLevel, RecurrenceRule


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
        start_time = event_data.start_time
        end_time = event_data.end_time
        
        # Convertir en datetime si ce sont des strings
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Format de date de début invalide")
        
        if isinstance(end_time, str):
            try:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Format de date de fin invalide")
        
        # Normaliser les dates pour la comparaison (enlever les fuseaux horaires si présents)
        if hasattr(start_time, 'replace') and start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        if hasattr(end_time, 'replace') and end_time.tzinfo is not None:
            end_time = end_time.replace(tzinfo=None)
            
        if start_time > end_time:
            raise HTTPException(status_code=400, detail="L'heure de début doit être avant ou égale à l'heure de fin")
        
        # Créer l'événement principal
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
            user_id=user_id
        )
        
        # Ajouter les données de récurrence si présentes
        if event_data.recurrence:
            recurrence = event_data.recurrence
            # Traiter la récurrence comme un dict (venant du JSON) ou un objet
            if isinstance(recurrence, dict):
                recurrence_data = recurrence
            else:
                recurrence_data = recurrence.__dict__
            
            db_event.recurrence_type = recurrence_data.get('type')
            db_event.recurrence_interval = recurrence_data.get('interval', 1)
            days_of_week = recurrence_data.get('daysOfWeek') or recurrence_data.get('days_of_week')
            db_event.recurrence_days = ','.join(map(str, days_of_week)) if days_of_week else None
            end_date = recurrence_data.get('endDate') or recurrence_data.get('end_date')
            db_event.recurrence_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
            db_event.recurrence_count = recurrence_data.get('count')
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        
        # Générer les événements récurrents si nécessaire
        if event_data.recurrence:
            # Convertir en RecurrenceRule ou dict pour la génération
            if isinstance(event_data.recurrence, dict):
                self._generate_recurring_events_from_dict(db_event, event_data.recurrence)
            else:
                self._generate_recurring_events(db_event, event_data.recurrence)
        
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
        
        # Gérer la récurrence séparément
        recurrence = update_data.pop("recurrence", None)
        
        # S'assurer que start_time est avant end_time si les deux sont fournis
        start_time = update_data.get("start_time", event.start_time)
        end_time = update_data.get("end_time", event.end_time)
        
        # Normaliser les dates pour la comparaison (enlever les fuseaux horaires si présents)
        if hasattr(start_time, 'replace') and start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        if hasattr(end_time, 'replace') and end_time.tzinfo is not None:
            end_time = end_time.replace(tzinfo=None)
            
        if start_time > end_time:
            raise HTTPException(status_code=400, detail="L'heure de début doit être avant ou égale à l'heure de fin")

        # Vérifier la catégorie si elle est modifiée
        if "category_id" in update_data:
            category = self.db.query(Category).filter(Category.id == update_data["category_id"]).first()
            if not category:
                raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        
        # Mettre à jour les champs de base
        for field, value in update_data.items():
            setattr(event, field, value)
            
        # Mettre à jour la récurrence
        if recurrence is not None:
            if recurrence:  # Si une récurrence est fournie
                # Traiter la récurrence comme un dict (venant du JSON)
                if isinstance(recurrence, dict):
                    recurrence_data = recurrence
                else:
                    recurrence_data = recurrence.__dict__
                
                event.recurrence_type = recurrence_data.get('type')
                event.recurrence_interval = recurrence_data.get('interval', 1)
                days_of_week = recurrence_data.get('daysOfWeek') or recurrence_data.get('days_of_week')
                event.recurrence_days = ','.join(map(str, days_of_week)) if days_of_week else None
                end_date = recurrence_data.get('endDate') or recurrence_data.get('end_date')
                event.recurrence_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
                event.recurrence_count = recurrence_data.get('count')
                
                # Supprimer les anciens événements récurrents enfants s'ils existent
                self.db.query(Event).filter(Event.parent_event_id == event.id).delete()
                self.db.commit()
                
                # Générer les nouveaux événements récurrents
                self._generate_recurring_events_from_dict(event, recurrence_data)
                
            else:  # Si la récurrence est supprimée
                event.recurrence_type = None
                event.recurrence_interval = None
                event.recurrence_days = None
                event.recurrence_end_date = None
                event.recurrence_count = None
                
                # Supprimer les événements récurrents enfants
                self.db.query(Event).filter(Event.parent_event_id == event.id).delete()
                self.db.commit()
        
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
    
    def _generate_recurring_events_from_dict(self, parent_event: Event, recurrence_dict: dict) -> None:
        """
        Génère les événements récurrents basés sur un dictionnaire de récurrence
        """
        events_to_create = []
        current_date = parent_event.start_time
        event_duration = parent_event.end_time - parent_event.start_time
        count = 0
        max_count = recurrence_dict.get('count') or 1000  # Limite de sécurité
        end_date = None
        
        end_date_str = recurrence_dict.get('endDate') or recurrence_dict.get('end_date')
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except:
                end_date = None
        
        recurrence_type = recurrence_dict.get('type')
        interval = recurrence_dict.get('interval', 1)
        days_of_week = recurrence_dict.get('daysOfWeek') or recurrence_dict.get('days_of_week')
        
        while count < max_count:
            # Calculer la prochaine occurrence
            if recurrence_type == "daily":
                if days_of_week:
                    # Récurrence quotidienne avec des jours spécifiques
                    next_date = self._get_next_weekday_occurrence(
                        current_date, days_of_week, interval
                    )
                else:
                    # Récurrence quotidienne simple
                    next_date = current_date + timedelta(days=interval)
            elif recurrence_type == "weekly":
                next_date = current_date + timedelta(weeks=interval)
            elif recurrence_type == "monthly":
                # Approximation pour les mois (30 jours)
                next_date = current_date + timedelta(days=30 * interval)
            elif recurrence_type == "yearly":
                # Approximation pour les années (365 jours)
                next_date = current_date + timedelta(days=365 * interval)
            else:
                break
            
            # Vérifier les conditions d'arrêt
            if end_date and next_date > end_date:
                break
            
            # Créer l'événement récurrent
            recurring_event = Event(
                title=parent_event.title,
                description=parent_event.description,
                start_time=next_date,
                end_time=next_date + event_duration,
                location=parent_event.location,
                priority=parent_event.priority,
                status=parent_event.status,
                is_flexible=parent_event.is_flexible,
                category_id=parent_event.category_id,
                user_id=parent_event.user_id,
                parent_event_id=parent_event.id,
                # Les événements enfants n'ont pas de récurrence propre
                recurrence_type=None,
                recurrence_interval=None,
                recurrence_days=None,
                recurrence_end_date=None,
                recurrence_count=None
            )
            
            events_to_create.append(recurring_event)
            current_date = next_date
            count += 1
        
        # Ajouter tous les événements récurrents en une fois
        if events_to_create:
            self.db.add_all(events_to_create)
            self.db.commit()
    
    def _generate_recurring_events(self, parent_event: Event, recurrence_rule: RecurrenceRule) -> None:
        """
        Génère les événements récurrents basés sur la règle de récurrence
        """
        events_to_create = []
        current_date = parent_event.start_time
        event_duration = parent_event.end_time - parent_event.start_time
        count = 0
        max_count = recurrence_rule.count or 1000  # Limite de sécurité
        end_date = datetime.fromisoformat(recurrence_rule.end_date) if recurrence_rule.end_date else None
        
        while count < max_count:
            # Calculer la prochaine occurrence
            if recurrence_rule.type == "daily":
                if recurrence_rule.days_of_week:
                    # Récurrence quotidienne avec des jours spécifiques
                    next_date = self._get_next_weekday_occurrence(
                        current_date, recurrence_rule.days_of_week, recurrence_rule.interval
                    )
                else:
                    # Récurrence quotidienne simple
                    next_date = current_date + timedelta(days=recurrence_rule.interval)
            elif recurrence_rule.type == "weekly":
                next_date = current_date + timedelta(weeks=recurrence_rule.interval)
            elif recurrence_rule.type == "monthly":
                # Approximation pour les mois (30 jours)
                next_date = current_date + timedelta(days=30 * recurrence_rule.interval)
            elif recurrence_rule.type == "yearly":
                # Approximation pour les années (365 jours)
                next_date = current_date + timedelta(days=365 * recurrence_rule.interval)
            else:
                break
            
            # Vérifier les conditions d'arrêt
            if end_date and next_date > end_date:
                break
            
            # Créer l'événement récurrent
            recurring_event = Event(
                title=parent_event.title,
                description=parent_event.description,
                start_time=next_date,
                end_time=next_date + event_duration,
                location=parent_event.location,
                priority=parent_event.priority,
                status=parent_event.status,
                is_flexible=parent_event.is_flexible,
                category_id=parent_event.category_id,
                user_id=parent_event.user_id,
                parent_event_id=parent_event.id,
                # Les événements enfants n'ont pas de récurrence propre
                recurrence_type=None,
                recurrence_interval=None,
                recurrence_days=None,
                recurrence_end_date=None,
                recurrence_count=None
            )
            
            events_to_create.append(recurring_event)
            current_date = next_date
            count += 1
        
        # Ajouter tous les événements récurrents en une fois
        if events_to_create:
            self.db.add_all(events_to_create)
            self.db.commit()
    
    def _get_next_weekday_occurrence(self, current_date: datetime, days_of_week: List[int], weeks_interval: int) -> datetime:
        """
        Trouve la prochaine occurrence pour une récurrence quotidienne avec des jours spécifiques
        """
        current_weekday = current_date.weekday()  # 0 = Lundi, 6 = Dimanche
        
        # Trouver le prochain jour dans la liste
        next_days = [d for d in days_of_week if d > current_weekday]
        
        if next_days:
            # Il y a un jour dans la même semaine
            days_to_add = min(next_days) - current_weekday
        else:
            # Passer à la semaine suivante (ou selon l'intervalle)
            days_to_add = (7 * weeks_interval) + min(days_of_week) - current_weekday
        
        return current_date + timedelta(days=days_to_add) 