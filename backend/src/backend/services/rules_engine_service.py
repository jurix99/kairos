"""
Service du moteur de règles pour générer des suggestions intelligentes
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from collections import defaultdict

from ..models.database import Event, Suggestion, Category
from ..models.schemas import SuggestionType, PriorityLevel, EventStatus


class RulesEngineService:
    """
    Service pour le moteur de règles qui génère des suggestions basées sur le calendrier
    """
    
    # Constantes pour les règles
    MAX_WORK_HOURS_BEFORE_BREAK = 3.0  # Heures de travail avant de suggérer une pause
    BREAK_DURATION_MINUTES = 15  # Durée de pause suggérée
    IMBALANCE_THRESHOLD = 0.4  # Seuil de déséquilibre (40%)
    POSTPONEMENT_THRESHOLD = 3  # Nombre de reports avant suggestion
    SUGGESTION_EXPIRY_HOURS = 24  # Durée de vie d'une suggestion en heures
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_suggestions_for_user(self, user_id: int, date: Optional[datetime] = None) -> List[Suggestion]:
        """
        Génère toutes les suggestions pour un utilisateur à une date donnée
        """
        if date is None:
            date = datetime.now()
        
        suggestions = []
        
        # Nettoyer les anciennes suggestions expirées
        self._cleanup_expired_suggestions(user_id)
        
        # Règle 1: Suggestion de pause
        break_suggestions = self._check_break_rule(user_id, date)
        suggestions.extend(break_suggestions)
        
        # Règle 2: Équilibre de la journée
        balance_suggestions = self._check_balance_rule(user_id, date)
        suggestions.extend(balance_suggestions)
        
        # Règle 3: Déplacement d'événements fréquemment reportés
        move_suggestions = self._check_postponement_rule(user_id)
        suggestions.extend(move_suggestions)
        
        # Sauvegarder les suggestions en base
        for suggestion in suggestions:
            self.db.add(suggestion)
        
        self.db.commit()
        
        return suggestions
    
    def _check_break_rule(self, user_id: int, date: datetime) -> List[Suggestion]:
        """
        Règle: Suggérer une pause après X heures de travail continu
        """
        suggestions = []
        
        # Récupérer les événements de la journée
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        events = self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.start_time >= start_of_day,
            Event.start_time < end_of_day,
            Event.status != EventStatus.CANCELLED
        ).order_by(Event.start_time).all()
        
        if not events:
            return suggestions
        
        # Analyser les blocs de travail continu
        current_block_start = None
        current_block_hours = 0.0
        last_event_end = None
        
        for event in events:
            # Normaliser les dates
            event_start = event.start_time.replace(tzinfo=None) if event.start_time.tzinfo else event.start_time
            event_end = event.end_time.replace(tzinfo=None) if event.end_time.tzinfo else event.end_time
            
            # Calculer la durée de l'événement en heures
            duration = (event_end - event_start).total_seconds() / 3600
            
            # Si c'est le premier événement ou s'il y a moins de 30 minutes depuis le dernier
            if current_block_start is None:
                current_block_start = event_start
                current_block_hours = duration
            elif last_event_end and (event_start - last_event_end).total_seconds() / 60 <= 30:
                # Continuer le bloc actuel
                current_block_hours += duration
            else:
                # Nouveau bloc, vérifier l'ancien
                if current_block_hours >= self.MAX_WORK_HOURS_BEFORE_BREAK:
                    # Vérifier si une suggestion similaire n'existe pas déjà
                    if not self._suggestion_exists(user_id, SuggestionType.TAKE_BREAK, current_block_start):
                        suggestion = self._create_break_suggestion(
                            user_id, 
                            current_block_hours, 
                            last_event_end
                        )
                        suggestions.append(suggestion)
                
                # Nouveau bloc
                current_block_start = event_start
                current_block_hours = duration
            
            last_event_end = event_end
        
        # Vérifier le dernier bloc
        if current_block_hours >= self.MAX_WORK_HOURS_BEFORE_BREAK:
            if not self._suggestion_exists(user_id, SuggestionType.TAKE_BREAK, current_block_start):
                suggestion = self._create_break_suggestion(
                    user_id, 
                    current_block_hours, 
                    last_event_end
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _check_balance_rule(self, user_id: int, date: datetime) -> List[Suggestion]:
        """
        Règle: Suggérer un rééquilibrage si la journée est déséquilibrée
        """
        suggestions = []
        
        # Récupérer les événements de la journée
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        events = self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.start_time >= start_of_day,
            Event.start_time < end_of_day,
            Event.status != EventStatus.CANCELLED
        ).all()
        
        if not events:
            return suggestions
        
        # Calculer la répartition du temps par catégorie
        category_hours = defaultdict(float)
        total_hours = 0.0
        
        for event in events:
            event_start = event.start_time.replace(tzinfo=None) if event.start_time.tzinfo else event.start_time
            event_end = event.end_time.replace(tzinfo=None) if event.end_time.tzinfo else event.end_time
            duration = (event_end - event_start).total_seconds() / 3600
            
            category = self.db.query(Category).filter(Category.id == event.category_id).first()
            if category:
                category_hours[category.name] += duration
                total_hours += duration
        
        if total_hours == 0:
            return suggestions
        
        # Calculer les pourcentages
        category_percentages = {
            cat: (hours / total_hours) 
            for cat, hours in category_hours.items()
        }
        
        # Détecter les déséquilibres (une catégorie > 60% ou travail > 80%)
        for category, percentage in category_percentages.items():
            if percentage > 0.6:  # Plus de 60% de la journée
                # Vérifier si une suggestion similaire n'existe pas déjà
                if not self._suggestion_exists(user_id, SuggestionType.BALANCE_DAY, start_of_day):
                    suggestion = self._create_balance_suggestion(
                        user_id,
                        category,
                        percentage,
                        category_hours,
                        start_of_day
                    )
                    suggestions.append(suggestion)
                    break  # Une seule suggestion de rééquilibrage par jour
        
        return suggestions
    
    def _check_postponement_rule(self, user_id: int) -> List[Suggestion]:
        """
        Règle: Suggérer de déplacer un événement si report fréquent
        """
        suggestions = []
        
        # Récupérer tous les événements avec leur historique de modifications
        # (On simule en regardant les événements modifiés récemment)
        now = datetime.now()
        last_week = now - timedelta(days=7)
        
        # Récupérer les événements récents
        events = self.db.query(Event).filter(
            Event.user_id == user_id,
            Event.updated_at >= last_week,
            Event.status != EventStatus.CANCELLED,
            Event.status != EventStatus.COMPLETED
        ).all()
        
        # Compter les modifications par événement (via updated_at vs created_at)
        for event in events:
            # Si l'événement a été mis à jour au moins 2 fois (updated_at != created_at)
            time_diff = (event.updated_at - event.created_at).total_seconds()
            
            # Si l'événement a été créé il y a plus d'un jour et mis à jour récemment
            # cela suggère des reports multiples
            if time_diff > 86400:  # Plus d'un jour de différence
                # Vérifier si c'est un événement flexible
                if event.is_flexible:
                    # Vérifier si une suggestion similaire n'existe pas déjà
                    if not self._suggestion_exists(
                        user_id, 
                        SuggestionType.MOVE_EVENT, 
                        event.start_time,
                        event.id
                    ):
                        suggestion = self._create_move_suggestion(
                            user_id,
                            event
                        )
                        suggestions.append(suggestion)
        
        return suggestions
    
    def _create_break_suggestion(
        self, 
        user_id: int, 
        hours_worked: float, 
        suggested_time: datetime
    ) -> Suggestion:
        """
        Crée une suggestion de pause
        """
        extra_data = {
            "hours_worked": round(hours_worked, 2),
            "suggested_break_duration": self.BREAK_DURATION_MINUTES,
            "suggested_time": suggested_time.isoformat() if suggested_time else None
        }
        
        return Suggestion(
            user_id=user_id,
            type=SuggestionType.TAKE_BREAK,
            title="💆 Temps de pause recommandé",
            description=f"Vous avez travaillé {round(hours_worked, 1)} heures consécutives. "
                       f"Il est recommandé de prendre une pause de {self.BREAK_DURATION_MINUTES} minutes "
                       f"pour maintenir votre productivité et votre bien-être.",
            priority=PriorityLevel.MEDIUM,
            rule_triggered="break_after_work_hours",
            extra_data=json.dumps(extra_data),
            expires_at=datetime.utcnow() + timedelta(hours=self.SUGGESTION_EXPIRY_HOURS)
        )
    
    def _create_balance_suggestion(
        self, 
        user_id: int,
        dominant_category: str,
        percentage: float,
        all_categories: Dict[str, float],
        date: datetime
    ) -> Suggestion:
        """
        Crée une suggestion d'équilibrage
        """
        extra_data = {
            "dominant_category": dominant_category,
            "percentage": round(percentage * 100, 1),
            "category_distribution": {
                cat: round(hours, 2) 
                for cat, hours in all_categories.items()
            },
            "date": date.isoformat()
        }
        
        other_categories = [cat for cat in all_categories.keys() if cat != dominant_category]
        other_cats_text = ", ".join(other_categories[:3]) if other_categories else "autres activités"
        
        return Suggestion(
            user_id=user_id,
            type=SuggestionType.BALANCE_DAY,
            title="⚖️ Rééquilibrer votre journée",
            description=f"Votre journée est fortement orientée vers '{dominant_category}' "
                       f"({round(percentage * 100, 1)}% de votre temps). "
                       f"Pensez à équilibrer avec {other_cats_text} pour une meilleure harmonie.",
            priority=PriorityLevel.LOW,
            rule_triggered="balance_day_categories",
            extra_data=json.dumps(extra_data),
            expires_at=datetime.utcnow() + timedelta(hours=self.SUGGESTION_EXPIRY_HOURS)
        )
    
    def _create_move_suggestion(
        self,
        user_id: int,
        event: Event
    ) -> Suggestion:
        """
        Crée une suggestion de déplacement d'événement
        """
        extra_data = {
            "event_id": event.id,
            "event_title": event.title,
            "current_start_time": event.start_time.isoformat(),
            "times_modified": "multiple"
        }
        
        return Suggestion(
            user_id=user_id,
            type=SuggestionType.MOVE_EVENT,
            title="📅 Événement à replanifier",
            description=f"L'événement '{event.title}' a été reporté plusieurs fois. "
                       f"Il serait peut-être temps de le replanifier à une date plus adaptée "
                       f"ou de reconsidérer sa priorité.",
            priority=PriorityLevel.MEDIUM,
            rule_triggered="frequent_postponement",
            extra_data=json.dumps(extra_data),
            related_event_id=event.id,
            expires_at=datetime.utcnow() + timedelta(hours=self.SUGGESTION_EXPIRY_HOURS)
        )
    
    def _suggestion_exists(
        self, 
        user_id: int, 
        suggestion_type: SuggestionType, 
        reference_time: datetime,
        event_id: Optional[int] = None
    ) -> bool:
        """
        Vérifie si une suggestion similaire existe déjà et est toujours active
        """
        query = self.db.query(Suggestion).filter(
            Suggestion.user_id == user_id,
            Suggestion.type == suggestion_type,
            Suggestion.status == "pending",
            Suggestion.expires_at > datetime.utcnow()
        )
        
        if event_id:
            query = query.filter(Suggestion.related_event_id == event_id)
        
        # Vérifier dans une fenêtre de temps (même journée)
        if reference_time:
            start_of_day = reference_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            query = query.filter(
                Suggestion.created_at >= start_of_day,
                Suggestion.created_at < end_of_day
            )
        
        return query.first() is not None
    
    def _cleanup_expired_suggestions(self, user_id: int) -> None:
        """
        Nettoie les suggestions expirées en changeant leur statut
        """
        self.db.query(Suggestion).filter(
            Suggestion.user_id == user_id,
            Suggestion.expires_at < datetime.utcnow(),
            Suggestion.status == "pending"
        ).update({"status": "expired"})
        
        self.db.commit()
    
    def get_active_suggestions(self, user_id: int) -> List[Suggestion]:
        """
        Récupère toutes les suggestions actives pour un utilisateur
        """
        self._cleanup_expired_suggestions(user_id)
        
        return self.db.query(Suggestion).filter(
            Suggestion.user_id == user_id,
            Suggestion.status == "pending",
            Suggestion.expires_at > datetime.utcnow()
        ).order_by(
            Suggestion.priority.desc(),
            Suggestion.created_at.desc()
        ).all()
    
    def update_suggestion_status(
        self, 
        suggestion_id: int, 
        user_id: int, 
        status: str
    ) -> Optional[Suggestion]:
        """
        Met à jour le statut d'une suggestion
        """
        suggestion = self.db.query(Suggestion).filter(
            Suggestion.id == suggestion_id,
            Suggestion.user_id == user_id
        ).first()
        
        if suggestion:
            suggestion.status = status
            self.db.commit()
            self.db.refresh(suggestion)
        
        return suggestion
    
    def get_suggestion_by_id(self, suggestion_id: int, user_id: int) -> Optional[Suggestion]:
        """
        Récupère une suggestion par son ID
        """
        return self.db.query(Suggestion).filter(
            Suggestion.id == suggestion_id,
            Suggestion.user_id == user_id
        ).first()

