"""
Tests pour le service de scheduling intelligent
"""

import pytest
from datetime import datetime, timedelta, time
from unittest.mock import Mock, MagicMock
from backend.services.smart_scheduler_service import (
    SmartSchedulerService,
    TimeConstraint,
    SmartSchedulingResult
)
from backend.models.database import Event
from backend.models.schemas import PriorityLevel


class TestTimeConstraint:
    """Tests pour TimeConstraint"""
    
    def test_morning_only_constraint(self):
        """Test: contrainte "matin seulement" """
        constraint = TimeConstraint(morning_only=True)
        
        # Matin (valide)
        assert constraint.is_valid_time(datetime(2025, 1, 1, 9, 0))
        
        # Après-midi (invalide)
        assert not constraint.is_valid_time(datetime(2025, 1, 1, 14, 0))
    
    def test_afternoon_only_constraint(self):
        """Test: contrainte "après-midi seulement" """
        constraint = TimeConstraint(afternoon_only=True)
        
        # Matin (invalide)
        assert not constraint.is_valid_time(datetime(2025, 1, 1, 9, 0))
        
        # Après-midi (valide)
        assert constraint.is_valid_time(datetime(2025, 1, 1, 14, 0))
    
    def test_evening_only_constraint(self):
        """Test: contrainte "soir seulement" """
        constraint = TimeConstraint(evening_only=True)
        
        # Après-midi (invalide)
        assert not constraint.is_valid_time(datetime(2025, 1, 1, 14, 0))
        
        # Soir (valide)
        assert constraint.is_valid_time(datetime(2025, 1, 1, 19, 0))
    
    def test_not_before_constraint(self):
        """Test: contrainte "pas avant" """
        constraint = TimeConstraint(not_before=time(10, 0))
        
        # Avant 10h (invalide)
        assert not constraint.is_valid_time(datetime(2025, 1, 1, 9, 0))
        
        # Après 10h (valide)
        assert constraint.is_valid_time(datetime(2025, 1, 1, 11, 0))
    
    def test_not_after_constraint(self):
        """Test: contrainte "pas après" """
        constraint = TimeConstraint(not_after=time(19, 0))
        
        # Avant 19h (valide)
        assert constraint.is_valid_time(datetime(2025, 1, 1, 18, 0))
        
        # Après 19h (invalide)
        assert not constraint.is_valid_time(datetime(2025, 1, 1, 20, 0))
    
    def test_combined_constraints(self):
        """Test: contraintes combinées"""
        constraint = TimeConstraint(
            not_before=time(9, 0),
            not_after=time(19, 0)
        )
        
        # Dans la plage (valide)
        assert constraint.is_valid_time(datetime(2025, 1, 1, 14, 0))
        
        # Avant la plage (invalide)
        assert not constraint.is_valid_time(datetime(2025, 1, 1, 8, 0))
        
        # Après la plage (invalide)
        assert not constraint.is_valid_time(datetime(2025, 1, 1, 20, 0))


class TestSmartSchedulerService:
    """Tests pour SmartSchedulerService"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.mock_db = Mock()
        self.service = SmartSchedulerService(self.mock_db)
    
    def test_detect_travel_conflicts_no_events(self):
        """Test: pas de conflits si pas d'événements"""
        # Mock: aucun événement
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        conflicts = self.service.detect_travel_conflicts(
            user_id=1,
            date=datetime(2025, 1, 1)
        )
        
        assert conflicts == []
    
    def test_detect_travel_conflicts_single_event(self):
        """Test: pas de conflits avec un seul événement"""
        # Mock: un seul événement
        event = Mock()
        event.id = 1
        event.title = "Meeting"
        event.location = "Paris"
        event.start_time = datetime(2025, 1, 1, 10, 0)
        event.end_time = datetime(2025, 1, 1, 11, 0)
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [event]
        
        conflicts = self.service.detect_travel_conflicts(
            user_id=1,
            date=datetime(2025, 1, 1)
        )
        
        assert conflicts == []
    
    def test_detect_travel_conflicts_insufficient_time(self):
        """Test: détection de conflit avec temps de trajet insuffisant"""
        # Créer deux événements avec temps de trajet insuffisant
        event1 = Mock()
        event1.id = 1
        event1.title = "Meeting Paris"
        event1.location = "Paris"
        event1.start_time = datetime(2025, 1, 1, 10, 0)
        event1.end_time = datetime(2025, 1, 1, 11, 0)
        
        event2 = Mock()
        event2.id = 2
        event2.title = "Meeting Lyon"
        event2.location = "Lyon"
        event2.start_time = datetime(2025, 1, 1, 11, 30)  # Seulement 30 min après
        event2.end_time = datetime(2025, 1, 1, 12, 30)
        event2.is_flexible = True
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1, event2
        ]
        
        conflicts = self.service.detect_travel_conflicts(
            user_id=1,
            date=datetime(2025, 1, 1)
        )
        
        # Devrait détecter un conflit
        assert len(conflicts) == 1
        assert conflicts[0]["current_event"]["id"] == 1
        assert conflicts[0]["next_event"]["id"] == 2
        assert "trajet" in conflicts[0]["message"].lower()
    
    def test_is_slot_available_no_conflicts(self):
        """Test: créneau disponible sans conflits"""
        # Mock: aucun événement en conflit
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        is_available = self.service._is_slot_available(
            user_id=1,
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 11, 0),
            location="Paris"
        )
        
        assert is_available is True
    
    def test_is_slot_available_direct_conflict(self):
        """Test: créneau non disponible avec conflit direct"""
        # Mock: événement en conflit direct
        conflicting_event = Mock()
        conflicting_event.start_time = datetime(2025, 1, 1, 10, 30)
        conflicting_event.end_time = datetime(2025, 1, 1, 11, 30)
        conflicting_event.location = "Paris"
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            conflicting_event
        ]
        
        is_available = self.service._is_slot_available(
            user_id=1,
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 11, 0),
            location="Paris"
        )
        
        assert is_available is False
    
    def test_group_by_location(self):
        """Test: groupement des événements par lieu"""
        event1 = Mock()
        event1.location = "Paris"
        
        event2 = Mock()
        event2.location = "Lyon"
        
        event3 = Mock()
        event3.location = "Paris"
        
        events = [event1, event2, event3]
        groups = self.service._group_by_location(events)
        
        assert len(groups) == 2
        assert len(groups["Paris"]) == 2
        assert len(groups["Lyon"]) == 1
    
    def test_calculate_slot_score_preferred_time(self):
        """Test: calcul du score d'un créneau proche du temps préféré"""
        preferred = datetime(2025, 1, 1, 10, 0)
        
        # Mock: pas d'événements proches
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        
        # Score pour le temps préféré exact
        score_exact = self.service._calculate_slot_score(
            user_id=1,
            start_time=preferred,
            end_time=preferred + timedelta(hours=1),
            location="Paris",
            preferred_start=preferred,
            day_offset=0
        )
        
        # Score pour 1 heure plus tard
        score_later = self.service._calculate_slot_score(
            user_id=1,
            start_time=preferred + timedelta(hours=1),
            end_time=preferred + timedelta(hours=2),
            location="Paris",
            preferred_start=preferred,
            day_offset=0
        )
        
        # Le score exact devrait être meilleur
        assert score_exact > score_later
    
    def test_optimize_event_sequence_no_flexible_events(self):
        """Test: pas d'optimisation possible sans événements flexibles"""
        # Mock: événements non flexibles
        event1 = Mock()
        event1.is_flexible = False
        
        event2 = Mock()
        event2.is_flexible = False
        
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            event1, event2
        ]
        
        result = self.service.optimize_event_sequence(
            user_id=1,
            date=datetime(2025, 1, 1)
        )
        
        assert result["optimization_possible"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
