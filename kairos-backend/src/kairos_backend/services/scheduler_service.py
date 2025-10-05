"""
Service de scheduling automatique pour l'agenda intelligent
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from ..models.database import Event
from ..models.schemas import PriorityLevel, ConflictSuggestion, SchedulingResult
from ..config.settings import settings


class SchedulerService:
    """
    Gestionnaire de scheduling automatique pour les événements
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_available_slot(
        self,
        duration: timedelta,
        preferred_start: datetime,
        priority: PriorityLevel,
        category_id: int,
        working_hours_start: Optional[int] = None,
        working_hours_end: Optional[int] = None,
        search_days: Optional[int] = None
    ) -> SchedulingResult:
        """
        Trouve un créneau disponible pour un nouvel événement
        
        Args:
            duration: Durée de l'événement
            preferred_start: Heure de début préférée
            priority: Priorité de l'événement
            category_id: ID de la catégorie
            working_hours_start: Heure de début des heures de travail
            working_hours_end: Heure de fin des heures de travail
            search_days: Nombre de jours à chercher
        
        Returns:
            SchedulingResult avec le créneau trouvé ou les conflits
        """
        
        # Utiliser les valeurs par défaut si non spécifiées
        working_hours_start = working_hours_start or settings.DEFAULT_WORKING_HOURS_START
        working_hours_end = working_hours_end or settings.DEFAULT_WORKING_HOURS_END
        search_days = search_days or settings.DEFAULT_SEARCH_DAYS
        
        # Vérifier d'abord si le créneau préféré est libre
        conflicts = self._check_conflicts(preferred_start, preferred_start + duration)
        
        if not conflicts:
            return SchedulingResult(
                success=True,
                scheduled_time=preferred_start,
                message="Créneau préféré disponible"
            )
        
        # Si conflit, essayer de résoudre selon la priorité
        if priority == PriorityLevel.HIGH:
            # Pour haute priorité, proposer de déplacer les événements flexibles
            suggestions = self._suggest_conflict_resolution(
                preferred_start, preferred_start + duration, conflicts
            )
            
            if suggestions:
                return SchedulingResult(
                    success=False,
                    conflicts=suggestions,
                    message="Conflits détectés - suggestions de résolution disponibles"
                )
        
        # Chercher un autre créneau disponible
        alternative_slot = self._find_alternative_slot(
            duration, preferred_start, working_hours_start, working_hours_end, search_days
        )
        
        if alternative_slot:
            return SchedulingResult(
                success=True,
                scheduled_time=alternative_slot,
                message=f"Créneau alternatif trouvé le {alternative_slot.strftime('%d/%m/%Y à %H:%M')}"
            )
        
        return SchedulingResult(
            success=False,
            message="Aucun créneau disponible trouvé dans les 7 prochains jours"
        )
    
    def _check_conflicts(self, start_time: datetime, end_time: datetime) -> List[Event]:
        """
        Vérifie les conflits avec les événements existants
        """
        return self.db.query(Event).filter(
            Event.start_time < end_time,
            Event.end_time > start_time
        ).all()
    
    def _suggest_conflict_resolution(
        self, 
        start_time: datetime, 
        end_time: datetime, 
        conflicts: List[Event]
    ) -> List[ConflictSuggestion]:
        """
        Suggère des résolutions pour les conflits détectés
        """
        suggestions = []
        
        for conflict in conflicts:
            if conflict.is_flexible and conflict.priority != PriorityLevel.HIGH:
                # Proposer de déplacer l'événement flexible
                
                # Option 1: Déplacer avant
                suggested_time = start_time - conflict.duration
                if suggested_time > datetime.now():
                    suggestions.append(ConflictSuggestion(
                        conflicting_event_id=conflict.id,
                        suggested_start_time=suggested_time,
                        reason=f"Déplacer '{conflict.title}' avant le nouvel événement"
                    ))
                
                # Option 2: Déplacer après
                suggested_time = end_time
                suggestions.append(ConflictSuggestion(
                    conflicting_event_id=conflict.id,
                    suggested_start_time=suggested_time,
                    reason=f"Déplacer '{conflict.title}' après le nouvel événement"
                ))
        
        return suggestions
    
    def _find_alternative_slot(
        self,
        duration: timedelta,
        preferred_start: datetime,
        working_hours_start: int,
        working_hours_end: int,
        search_days: int
    ) -> Optional[datetime]:
        """
        Trouve un créneau alternatif dans les heures de travail
        """
        current_date = preferred_start.date()
        
        for day_offset in range(search_days):
            search_date = current_date + timedelta(days=day_offset)
            
            # Commencer à l'heure préférée le premier jour, sinon aux heures de travail
            if day_offset == 0:
                start_hour = max(preferred_start.hour, working_hours_start)
            else:
                start_hour = working_hours_start
            
            current_time = datetime.combine(search_date, datetime.min.time()).replace(
                hour=start_hour, minute=0
            )
            
            end_of_day = datetime.combine(search_date, datetime.min.time()).replace(
                hour=working_hours_end, minute=0
            )
            
            # Chercher par créneaux configurables
            slot_duration = timedelta(minutes=settings.SLOT_DURATION_MINUTES)
            while current_time + duration <= end_of_day:
                if not self._check_conflicts(current_time, current_time + duration):
                    return current_time
                
                current_time += slot_duration
        
        return None
    
    def apply_conflict_resolution(self, suggestion: ConflictSuggestion) -> bool:
        """
        Applique une suggestion de résolution de conflit
        """
        try:
            event = self.db.query(Event).filter(Event.id == suggestion.conflicting_event_id).first()
            if event and event.is_flexible:
                # Calculer la nouvelle heure de fin
                duration = event.end_time - event.start_time
                event.start_time = suggestion.suggested_start_time
                event.end_time = suggestion.suggested_start_time + duration
                
                self.db.commit()
                return True
        except Exception:
            self.db.rollback()
        
        return False
    
    def get_daily_schedule(self, date: datetime) -> List[Event]:
        """
        Récupère le planning d'une journée
        """
        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.db.query(Event).options(joinedload(Event.category)).filter(
            Event.start_time >= start_of_day,
            Event.start_time < end_of_day
        ).order_by(Event.start_time).all()
    
    def get_weekly_schedule(self, start_date: datetime) -> dict[str, List[Event]]:
        """
        Récupère le planning d'une semaine
        """
        weekly_schedule = {}
        
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_key = current_date.strftime("%Y-%m-%d")
            weekly_schedule[day_key] = self.get_daily_schedule(current_date)
        
        return weekly_schedule 