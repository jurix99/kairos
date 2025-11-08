"""
Service de scheduling intelligent avec optimisation géographique et gestion des temps de trajet
"""

from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from ..models.database import Event
from ..models.schemas import PriorityLevel, EventCreate
from .travel_service import TravelService
from ..config.settings import settings


class TimeConstraint:
    """Représente une contrainte de temps pour le scheduling"""
    
    def __init__(
        self,
        not_before: Optional[time] = None,
        not_after: Optional[time] = None,
        morning_only: bool = False,
        afternoon_only: bool = False,
        evening_only: bool = False
    ):
        self.not_before = not_before
        self.not_after = not_after
        self.morning_only = morning_only
        self.afternoon_only = afternoon_only
        self.evening_only = evening_only
    
    def is_valid_time(self, dt: datetime) -> bool:
        """Vérifie si un datetime satisfait les contraintes"""
        hour = dt.hour
        
        # Vérifier les contraintes de période
        if self.morning_only and not (6 <= hour < 12):
            return False
        if self.afternoon_only and not (12 <= hour < 18):
            return False
        if self.evening_only and not (18 <= hour < 22):
            return False
        
        # Vérifier les contraintes horaires
        if self.not_before and dt.time() < self.not_before:
            return False
        if self.not_after and dt.time() > self.not_after:
            return False
        
        return True


class SmartSchedulingResult:
    """Résultat du scheduling intelligent avec informations détaillées"""
    
    def __init__(
        self,
        success: bool,
        scheduled_time: Optional[datetime] = None,
        message: str = "",
        travel_warnings: List[Dict] = None,
        conflicts: List[Dict] = None,
        optimization_applied: bool = False
    ):
        self.success = success
        self.scheduled_time = scheduled_time
        self.message = message
        self.travel_warnings = travel_warnings or []
        self.conflicts = conflicts or []
        self.optimization_applied = optimization_applied


class SmartSchedulerService:
    """
    Service de scheduling intelligent qui prend en compte:
    - Les disponibilités
    - Les lieux et temps de trajet
    - Les priorités
    - Les durées
    - Les contraintes horaires personnalisées
    """
    
    def __init__(self, db: Session):
        self.db = db
        # Initialiser le service de trajet avec les paramètres de configuration
        self.travel_service = TravelService(
            api_provider=settings.TRAVEL_API_PROVIDER,
            api_key=settings.TRAVEL_API_KEY,
            use_api=settings.USE_TRAVEL_API
        )
    
    def find_best_slot(
        self,
        user_id: int,
        duration: timedelta,
        preferred_start: datetime,
        priority: PriorityLevel,
        location: Optional[str] = None,
        category_id: Optional[int] = None,
        constraints: Optional[TimeConstraint] = None,
        search_days: int = 7
    ) -> SmartSchedulingResult:
        """
        Trouve le meilleur créneau pour un événement en tenant compte de tous les facteurs
        
        Args:
            user_id: ID de l'utilisateur
            duration: Durée de l'événement
            preferred_start: Heure de début préférée
            priority: Priorité de l'événement
            location: Lieu de l'événement
            category_id: ID de la catégorie
            constraints: Contraintes horaires
            search_days: Nombre de jours à chercher
        
        Returns:
            SmartSchedulingResult avec le créneau optimal trouvé
        """
        constraints = constraints or TimeConstraint()
        
        # Vérifier d'abord si le créneau préféré est disponible
        if self._is_slot_available(
            user_id, preferred_start, preferred_start + duration, location
        ) and constraints.is_valid_time(preferred_start):
            # Vérifier les conflits de déplacement
            travel_warnings = self._check_travel_conflicts(
                user_id, preferred_start, preferred_start + duration, location
            )
            
            if not travel_warnings or priority == PriorityLevel.HIGH:
                return SmartSchedulingResult(
                    success=True,
                    scheduled_time=preferred_start,
                    message="Créneau préféré disponible",
                    travel_warnings=travel_warnings
                )
        
        # Chercher un créneau alternatif optimal
        best_slot = self._find_optimal_slot(
            user_id, duration, preferred_start, location, 
            priority, constraints, search_days
        )
        
        if best_slot:
            return best_slot
        
        return SmartSchedulingResult(
            success=False,
            message=f"Aucun créneau disponible trouvé dans les {search_days} prochains jours"
        )
    
    def detect_travel_conflicts(
        self,
        user_id: int,
        date: datetime
    ) -> List[Dict]:
        """
        Détecte les conflits logistiques dus aux temps de trajet pour une journée
        
        Args:
            user_id: ID de l'utilisateur
            date: Date à analyser
        
        Returns:
            Liste des conflits détectés avec suggestions
        """
        # Récupérer tous les événements du jour triés par heure
        events = self._get_day_events(user_id, date)
        
        if len(events) < 2:
            return []
        
        conflicts = []
        
        for i in range(len(events) - 1):
            current_event = events[i]
            next_event = events[i + 1]
            
            # Calculer le temps de trajet nécessaire
            travel_time = self.travel_service.calculate_travel_time(
                current_event.location, next_event.location
            )
            
            # Calculer le temps disponible entre les deux événements
            available_time = next_event.start_time - current_event.end_time
            
            # Si le temps de trajet est supérieur au temps disponible
            if travel_time > available_time:
                shortage = travel_time - available_time
                shortage_minutes = int(shortage.total_seconds() / 60)
                travel_minutes = int(travel_time.total_seconds() / 60)
                
                # Proposer un nouveau créneau
                suggested_time = current_event.end_time + travel_time
                
                conflicts.append({
                    "current_event": {
                        "id": current_event.id,
                        "title": current_event.title,
                        "end_time": current_event.end_time.isoformat(),
                        "location": current_event.location
                    },
                    "next_event": {
                        "id": next_event.id,
                        "title": next_event.title,
                        "start_time": next_event.start_time.isoformat(),
                        "location": next_event.location,
                        "is_flexible": next_event.is_flexible
                    },
                    "conflict": {
                        "travel_time_minutes": travel_minutes,
                        "shortage_minutes": shortage_minutes,
                        "suggested_new_time": suggested_time.isoformat()
                    },
                    "message": (
                        f"Ton trajet entre '{current_event.location}' et "
                        f"'{next_event.location}' prend {travel_minutes} min, "
                        f"veux-tu que je déplace '{next_event.title}' à "
                        f"{suggested_time.strftime('%H:%M')} ?"
                    )
                })
        
        return conflicts
    
    def optimize_event_sequence(
        self,
        user_id: int,
        date: datetime,
        minimize_travel: bool = True
    ) -> Dict:
        """
        Optimise l'enchaînement des événements d'une journée
        
        Args:
            user_id: ID de l'utilisateur
            date: Date à optimiser
            minimize_travel: Si True, minimise les déplacements
        
        Returns:
            Dictionnaire avec les optimisations proposées
        """
        events = self._get_day_events(user_id, date)
        flexible_events = [e for e in events if e.is_flexible]
        
        if len(flexible_events) < 2:
            return {
                "optimization_possible": False,
                "message": "Pas assez d'événements flexibles pour optimiser"
            }
        
        # Grouper les événements par lieu
        location_groups = self._group_by_location(flexible_events)
        
        # Calculer le temps de trajet actuel
        current_travel_time = self._calculate_total_travel_time(events)
        
        # Proposer un réarrangement optimal
        optimized_events = self._optimize_by_location(flexible_events, events)
        optimized_travel_time = self._calculate_total_travel_time(optimized_events)
        
        savings = current_travel_time - optimized_travel_time
        
        if savings.total_seconds() > 600:  # Au moins 10 minutes d'économie
            return {
                "optimization_possible": True,
                "current_travel_minutes": int(current_travel_time.total_seconds() / 60),
                "optimized_travel_minutes": int(optimized_travel_time.total_seconds() / 60),
                "savings_minutes": int(savings.total_seconds() / 60),
                "suggestions": self._generate_reorganization_suggestions(
                    events, optimized_events
                ),
                "message": (
                    f"Je peux réorganiser tes événements pour économiser "
                    f"{int(savings.total_seconds() / 60)} min de déplacement"
                )
            }
        
        return {
            "optimization_possible": False,
            "message": "L'organisation actuelle est déjà optimale"
        }
    
    def _is_slot_available(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        location: Optional[str] = None
    ) -> bool:
        """Vérifie si un créneau est disponible en tenant compte du temps de trajet"""
        # Chercher les événements qui pourraient entrer en conflit
        events = self.db.query(Event).filter(
            Event.user_id == user_id,
            or_(
                and_(Event.start_time < end_time, Event.end_time > start_time),
                and_(Event.start_time < start_time, Event.end_time > start_time)
            )
        ).order_by(Event.start_time).all()
        
        if not events:
            return True
        
        # Vérifier chaque événement
        for event in events:
            # Conflit direct
            if event.start_time < end_time and event.end_time > start_time:
                return False
            
            # Conflit de déplacement avant
            if event.end_time <= start_time and location and event.location:
                travel_time = self.travel_service.calculate_travel_time(
                    event.location, location
                )
                if event.end_time + travel_time > start_time:
                    return False
            
            # Conflit de déplacement après
            if event.start_time >= end_time and location and event.location:
                travel_time = self.travel_service.calculate_travel_time(
                    location, event.location
                )
                if end_time + travel_time > event.start_time:
                    return False
        
        return True
    
    def _check_travel_conflicts(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        location: Optional[str]
    ) -> List[Dict]:
        """Vérifie les conflits de déplacement potentiels"""
        if not location:
            return []
        
        warnings = []
        
        # Événement avant
        prev_event = self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.end_time <= start_time
        ).order_by(Event.end_time.desc()).first()
        
        if prev_event and prev_event.location:
            travel_time = self.travel_service.calculate_travel_time(
                prev_event.location, location
            )
            available_time = start_time - prev_event.end_time
            
            if travel_time > available_time:
                warnings.append({
                    "type": "insufficient_travel_time_before",
                    "event": prev_event.title,
                    "travel_minutes": int(travel_time.total_seconds() / 60),
                    "available_minutes": int(available_time.total_seconds() / 60)
                })
        
        # Événement après
        next_event = self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.start_time >= end_time
        ).order_by(Event.start_time).first()
        
        if next_event and next_event.location:
            travel_time = self.travel_service.calculate_travel_time(
                location, next_event.location
            )
            available_time = next_event.start_time - end_time
            
            if travel_time > available_time:
                warnings.append({
                    "type": "insufficient_travel_time_after",
                    "event": next_event.title,
                    "travel_minutes": int(travel_time.total_seconds() / 60),
                    "available_minutes": int(available_time.total_seconds() / 60)
                })
        
        return warnings
    
    def _find_optimal_slot(
        self,
        user_id: int,
        duration: timedelta,
        preferred_start: datetime,
        location: Optional[str],
        priority: PriorityLevel,
        constraints: TimeConstraint,
        search_days: int
    ) -> Optional[SmartSchedulingResult]:
        """Trouve le créneau optimal avec scoring"""
        best_slot = None
        best_score = -1
        
        current_date = preferred_start.date()
        
        for day_offset in range(search_days):
            search_date = current_date + timedelta(days=day_offset)
            
            # Déterminer les heures de recherche
            start_hour = 8 if day_offset > 0 else max(preferred_start.hour, 8)
            end_hour = 20
            
            current_time = datetime.combine(search_date, time(hour=start_hour))
            end_of_search = datetime.combine(search_date, time(hour=end_hour))
            
            # Chercher par créneaux de 15 minutes
            while current_time + duration <= end_of_search:
                if not constraints.is_valid_time(current_time):
                    current_time += timedelta(minutes=15)
                    continue
                
                if self._is_slot_available(user_id, current_time, current_time + duration, location):
                    # Calculer le score de ce créneau
                    score = self._calculate_slot_score(
                        user_id, current_time, current_time + duration,
                        location, preferred_start, day_offset
                    )
                    
                    if score > best_score:
                        best_score = score
                        travel_warnings = self._check_travel_conflicts(
                            user_id, current_time, current_time + duration, location
                        )
                        best_slot = SmartSchedulingResult(
                            success=True,
                            scheduled_time=current_time,
                            message=f"Créneau optimal trouvé le {current_time.strftime('%d/%m/%Y à %H:%M')}",
                            travel_warnings=travel_warnings,
                            optimization_applied=True
                        )
                
                current_time += timedelta(minutes=15)
        
        return best_slot
    
    def _calculate_slot_score(
        self,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        location: Optional[str],
        preferred_start: datetime,
        day_offset: int
    ) -> float:
        """Calcule un score pour un créneau (plus élevé = meilleur)"""
        score = 100.0
        
        # Pénalité pour l'éloignement du temps préféré
        time_diff = abs((start_time - preferred_start).total_seconds())
        score -= min(time_diff / 3600, 50)  # Max 50 points de pénalité
        
        # Bonus si proche géographiquement des autres événements
        if location:
            nearby_events = self._get_nearby_events(user_id, start_time, location)
            score += len(nearby_events) * 10
        
        # Pénalité pour jour éloigné
        score -= day_offset * 5
        
        return score
    
    def _get_day_events(self, user_id: int, date: datetime) -> List[Event]:
        """Récupère tous les événements d'une journée triés par heure"""
        start_of_day = datetime.combine(date.date(), time.min)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.start_time >= start_of_day,
            Event.start_time < end_of_day
        ).order_by(Event.start_time).all()
    
    def _get_nearby_events(
        self,
        user_id: int,
        reference_time: datetime,
        location: str,
        max_distance_minutes: int = 30
    ) -> List[Event]:
        """Trouve les événements proches géographiquement"""
        nearby = []
        same_day_events = self._get_day_events(user_id, reference_time)
        
        for event in same_day_events:
            if event.location:
                travel_time = self.travel_service.calculate_travel_time(
                    location, event.location
                )
                if travel_time.total_seconds() / 60 <= max_distance_minutes:
                    nearby.append(event)
        
        return nearby
    
    def _group_by_location(self, events: List[Event]) -> Dict[str, List[Event]]:
        """Groupe les événements par lieu"""
        groups = {}
        for event in events:
            loc = event.location or "Aucun lieu"
            if loc not in groups:
                groups[loc] = []
            groups[loc].append(event)
        return groups
    
    def _calculate_total_travel_time(self, events: List[Event]) -> timedelta:
        """Calcule le temps de trajet total pour une séquence d'événements"""
        total = timedelta(0)
        
        for i in range(len(events) - 1):
            travel = self.travel_service.calculate_travel_time(
                events[i].location, events[i + 1].location
            )
            total += travel
        
        return total
    
    def _optimize_by_location(
        self,
        flexible_events: List[Event],
        all_events: List[Event]
    ) -> List[Event]:
        """
        Réorganise les événements flexibles pour minimiser les déplacements
        Cette fonction est une version simplifiée. Une version plus avancée 
        utiliserait un algorithme de type voyageur de commerce (TSP)
        """
        # Pour l'instant, on retourne les événements tels quels
        # Dans une vraie implémentation, on réorganiserait les événements flexibles
        return all_events
    
    def _generate_reorganization_suggestions(
        self,
        current: List[Event],
        optimized: List[Event]
    ) -> List[Dict]:
        """Génère des suggestions de réorganisation"""
        suggestions = []
        # Comparer les deux séquences et générer des suggestions
        # Implémentation simplifiée pour l'instant
        return suggestions
