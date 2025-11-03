"""
Tests pour le moteur de règles de suggestions
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.database import Base, User, Category, Event, Suggestion
from backend.models.schemas import EventStatus, PriorityLevel
from backend.services.rules_engine_service import RulesEngineService


# Fixture pour la base de données de test
@pytest.fixture
def db_session():
    """Crée une session de base de données en mémoire pour les tests"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(db_session):
    """Crée un utilisateur de test"""
    user = User(
        external_id="test_user_123",
        name="Test User",
        email="test@example.com",
        provider="google"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_category(db_session):
    """Crée une catégorie de test"""
    category = Category(
        name="Travail",
        color_code="#8B5CF6",
        description="Tâches professionnelles"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def test_break_rule_trigger(db_session, test_user, test_category):
    """
    Test: La règle de pause doit se déclencher après 3h de travail continu
    """
    # Créer des événements représentant 4 heures de travail continu
    now = datetime.now()
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Premier événement: 9h-11h (2 heures)
    event1 = Event(
        title="Réunion d'équipe",
        start_time=start_time,
        end_time=start_time + timedelta(hours=2),
        category_id=test_category.id,
        user_id=test_user.id,
        priority=PriorityLevel.HIGH,
        status=EventStatus.PENDING,
        is_flexible=False
    )
    db_session.add(event1)
    
    # Deuxième événement: 11h-13h (2 heures, donc total 4 heures)
    event2 = Event(
        title="Développement",
        start_time=start_time + timedelta(hours=2),
        end_time=start_time + timedelta(hours=4),
        category_id=test_category.id,
        user_id=test_user.id,
        priority=PriorityLevel.MEDIUM,
        status=EventStatus.PENDING,
        is_flexible=True
    )
    db_session.add(event2)
    db_session.commit()
    
    # Générer les suggestions
    rules_service = RulesEngineService(db_session)
    suggestions = rules_service.generate_suggestions_for_user(test_user.id, start_time)
    
    # Vérifier qu'une suggestion de pause a été générée
    break_suggestions = [s for s in suggestions if s.type == "take_break"]
    assert len(break_suggestions) > 0, "Une suggestion de pause devrait être générée"
    assert "4" in break_suggestions[0].description or "heures" in break_suggestions[0].description


def test_balance_rule_trigger(db_session, test_user, test_category):
    """
    Test: La règle d'équilibrage doit se déclencher si une catégorie > 60%
    """
    # Créer une deuxième catégorie
    category2 = Category(
        name="Personnel",
        color_code="#06B6D4",
        description="Activités personnelles"
    )
    db_session.add(category2)
    db_session.commit()
    
    now = datetime.now()
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # 6 heures de travail (75% d'une journée de 8h)
    event1 = Event(
        title="Travail intensif",
        start_time=start_time,
        end_time=start_time + timedelta(hours=6),
        category_id=test_category.id,
        user_id=test_user.id,
        priority=PriorityLevel.HIGH,
        status=EventStatus.PENDING,
        is_flexible=False
    )
    db_session.add(event1)
    
    # 2 heures d'activités personnelles (25%)
    event2 = Event(
        title="Sport",
        start_time=start_time + timedelta(hours=6),
        end_time=start_time + timedelta(hours=8),
        category_id=category2.id,
        user_id=test_user.id,
        priority=PriorityLevel.MEDIUM,
        status=EventStatus.PENDING,
        is_flexible=True
    )
    db_session.add(event2)
    db_session.commit()
    
    # Générer les suggestions
    rules_service = RulesEngineService(db_session)
    suggestions = rules_service.generate_suggestions_for_user(test_user.id, start_time)
    
    # Vérifier qu'une suggestion d'équilibrage a été générée
    balance_suggestions = [s for s in suggestions if s.type == "balance_day"]
    assert len(balance_suggestions) > 0, "Une suggestion d'équilibrage devrait être générée"
    assert "Travail" in balance_suggestions[0].description


def test_move_event_rule_trigger(db_session, test_user, test_category):
    """
    Test: La règle de déplacement doit se déclencher pour les événements reportés
    """
    # Créer un événement qui a été modifié plusieurs fois
    now = datetime.now()
    created_at = now - timedelta(days=3)
    
    event = Event(
        title="Tâche reportée",
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=1),
        category_id=test_category.id,
        user_id=test_user.id,
        priority=PriorityLevel.MEDIUM,
        status=EventStatus.PENDING,
        is_flexible=True,
        created_at=created_at,
        updated_at=now  # Mis à jour récemment
    )
    db_session.add(event)
    db_session.commit()
    
    # Générer les suggestions
    rules_service = RulesEngineService(db_session)
    suggestions = rules_service.generate_suggestions_for_user(test_user.id)
    
    # Vérifier qu'une suggestion de déplacement a été générée
    move_suggestions = [s for s in suggestions if s.type == "move_event"]
    assert len(move_suggestions) > 0, "Une suggestion de déplacement devrait être générée"
    assert event.title in move_suggestions[0].description


def test_no_duplicate_suggestions(db_session, test_user, test_category):
    """
    Test: Le système ne doit pas créer de suggestions en double
    """
    now = datetime.now()
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Créer un événement long pour déclencher une suggestion de pause
    event = Event(
        title="Travail continu",
        start_time=start_time,
        end_time=start_time + timedelta(hours=4),
        category_id=test_category.id,
        user_id=test_user.id,
        priority=PriorityLevel.HIGH,
        status=EventStatus.PENDING,
        is_flexible=False
    )
    db_session.add(event)
    db_session.commit()
    
    # Générer les suggestions une première fois
    rules_service = RulesEngineService(db_session)
    suggestions1 = rules_service.generate_suggestions_for_user(test_user.id, start_time)
    count1 = len(suggestions1)
    
    # Générer les suggestions une deuxième fois
    suggestions2 = rules_service.generate_suggestions_for_user(test_user.id, start_time)
    count2 = len(suggestions2)
    
    # Le nombre de suggestions ne doit pas augmenter
    assert count2 == 0, "Aucune nouvelle suggestion en double ne devrait être créée"


def test_suggestion_expiry(db_session, test_user, test_category):
    """
    Test: Les suggestions expirées doivent être marquées comme telles
    """
    now = datetime.now()
    
    # Créer une suggestion expirée
    suggestion = Suggestion(
        type="take_break",
        title="Test",
        description="Test suggestion",
        priority=PriorityLevel.MEDIUM,
        status="pending",
        rule_triggered="test_rule",
        user_id=test_user.id,
        created_at=now - timedelta(days=2),
        expires_at=now - timedelta(hours=1)  # Expirée il y a 1 heure
    )
    db_session.add(suggestion)
    db_session.commit()
    
    # Récupérer les suggestions actives
    rules_service = RulesEngineService(db_session)
    active_suggestions = rules_service.get_active_suggestions(test_user.id)
    
    # La suggestion expirée ne doit pas apparaître
    assert len(active_suggestions) == 0, "Les suggestions expirées ne doivent pas être actives"
    
    # Vérifier que le statut a été mis à jour
    db_session.refresh(suggestion)
    assert suggestion.status == "expired", "La suggestion doit être marquée comme expirée"


def test_update_suggestion_status(db_session, test_user):
    """
    Test: Le statut d'une suggestion peut être mis à jour
    """
    # Créer une suggestion
    suggestion = Suggestion(
        type="take_break",
        title="Test",
        description="Test suggestion",
        priority=PriorityLevel.MEDIUM,
        status="pending",
        rule_triggered="test_rule",
        user_id=test_user.id,
        expires_at=datetime.now() + timedelta(hours=24)
    )
    db_session.add(suggestion)
    db_session.commit()
    db_session.refresh(suggestion)
    
    # Mettre à jour le statut
    rules_service = RulesEngineService(db_session)
    updated = rules_service.update_suggestion_status(
        suggestion.id,
        test_user.id,
        "accepted"
    )
    
    assert updated is not None, "La suggestion devrait être mise à jour"
    assert updated.status == "accepted", "Le statut devrait être 'accepted'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

