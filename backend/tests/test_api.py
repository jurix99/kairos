"""
Tests pour l'API Kairos Backend
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.app import app
from src.backend.config.database import get_db, init_default_categories
from src.backend.models.database import Base

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la fonction get_db pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Fixture pour configurer la base de données de test"""
    Base.metadata.create_all(bind=engine)
    
    # Initialiser les catégories par défaut
    db = TestingSessionLocal()
    try:
        init_default_categories(db)
    finally:
        db.close()
    
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test de la route de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test de la route racine"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()


def test_get_categories(setup_database):
    """Test de récupération des catégories"""
    response = client.get("/categories/")
    assert response.status_code == 200
    categories = response.json()
    # Vérifier que les catégories par défaut sont présentes
    assert len(categories) >= 4
    category_names = [cat["name"] for cat in categories]
    assert "Travail" in category_names
    assert "Perso" in category_names


def test_create_category(setup_database):
    """Test de création d'une catégorie"""
    category_data = {
        "name": "Test Category",
        "color_code": "#FF5733",
        "description": "Une catégorie de test"
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 200
    
    created_category = response.json()
    assert created_category["name"] == category_data["name"]
    assert created_category["color_code"] == category_data["color_code"]
    assert "id" in created_category


def test_create_event(setup_database):
    """Test de création d'un événement"""
    # D'abord récupérer une catégorie existante
    categories_response = client.get("/categories/")
    categories = categories_response.json()
    assert len(categories) > 0, "Aucune catégorie disponible pour le test"
    category_id = categories[0]["id"]
    
    # Créer un événement
    event_data = {
        "title": "Réunion de test",
        "description": "Une réunion de test",
        "start_time": "2024-01-15T10:00:00",
        "duration_minutes": 60,
        "location": "Salle de réunion",
        "priority": "medium",
        "is_flexible": True,
        "category_id": category_id
    }
    
    response = client.post("/events/", json=event_data)
    assert response.status_code == 200
    
    created_event = response.json()
    assert created_event["title"] == event_data["title"]
    assert created_event["duration_minutes"] == event_data["duration_minutes"]
    assert "id" in created_event
    assert "end_time" in created_event


def test_schedule_event(setup_database):
    """Test du scheduling automatique"""
    # Récupérer une catégorie
    categories_response = client.get("/categories/")
    categories = categories_response.json()
    assert len(categories) > 0, "Aucune catégorie disponible pour le test"
    category_id = categories[0]["id"]
    
    # Essayer de planifier un événement
    event_data = {
        "title": "Événement planifié",
        "description": "Test de planification automatique",
        "start_time": "2024-01-15T14:00:00",
        "duration_minutes": 90,
        "priority": "high",
        "is_flexible": True,
        "category_id": category_id
    }
    
    response = client.post("/schedule/auto", json=event_data)
    assert response.status_code == 200
    
    result = response.json()
    assert "success" in result
    assert "message" in result


def test_get_events(setup_database):
    """Test de récupération des événements"""
    response = client.get("/events/")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)


def test_daily_schedule(setup_database):
    """Test du planning quotidien"""
    date = "2024-01-15T00:00:00"
    response = client.get(f"/schedule/daily?date={date}")
    assert response.status_code == 200
    
    schedule = response.json()
    assert "date" in schedule
    assert "events" in schedule
    assert isinstance(schedule["events"], list)


def test_check_conflicts(setup_database):
    """Test de vérification des conflits"""
    start_time = "2024-01-15T10:00:00"
    duration_minutes = 60
    
    response = client.get(f"/schedule/conflicts/check?start_time={start_time}&duration_minutes={duration_minutes}")
    assert response.status_code == 200
    
    result = response.json()
    assert "has_conflicts" in result
    assert "conflicts_count" in result
    assert "conflicting_events" in result


def test_get_availability(setup_database):
    """Test de récupération des créneaux disponibles"""
    date = "2024-01-15T00:00:00"
    
    response = client.get(f"/schedule/availability?date={date}")
    assert response.status_code == 200
    
    result = response.json()
    assert "date" in result
    assert "available_slots" in result
    assert "total_slots" in result


def test_event_statistics(setup_database):
    """Test des statistiques d'événements"""
    response = client.get("/events/statistics/overview")
    assert response.status_code == 200
    
    stats = response.json()
    assert "total_events" in stats
    assert "flexible_events" in stats
    assert "priority_distribution" in stats


def test_category_statistics(setup_database):
    """Test des statistiques de catégorie"""
    # Récupérer une catégorie
    categories_response = client.get("/categories/")
    categories = categories_response.json()
    assert len(categories) > 0, "Aucune catégorie disponible pour le test"
    category_id = categories[0]["id"]
    
    response = client.get(f"/categories/{category_id}/statistics")
    assert response.status_code == 200
    
    stats = response.json()
    assert "category_id" in stats
    assert "total_events" in stats 