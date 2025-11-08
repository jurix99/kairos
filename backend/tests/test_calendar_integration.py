"""
Tests pour le service d'intégration de calendrier
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.kairos_backend.models.database import Base, User, Category, CalendarIntegration
from src.kairos_backend.models.schemas import (
    CalendarIntegrationCreate,
    CalendarIntegrationUpdate,
    CalendarProvider,
)
from src.kairos_backend.services.calendar_integration_service import (
    CalendarIntegrationService,
)

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integrations.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def setup_database():
    """Fixture pour configurer la base de données de test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Fixture pour créer une session de base de données"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(db_session):
    """Fixture pour créer un utilisateur de test"""
    user = User(
        external_id="test_user_123",
        name="Test User",
        email="test@example.com",
        provider="github",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_category(db_session, test_user):
    """Fixture pour créer une catégorie de test"""
    category = Category(
        name="Test Category",
        color_code="#FF5733",
        description="Test category for integration tests",
        user_id=test_user.id,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


class TestCalendarIntegrationService:
    """Tests pour CalendarIntegrationService"""

    def test_create_integration_invalid_url(self, db_session, test_user):
        """Test de création d'une intégration avec une URL invalide"""
        service = CalendarIntegrationService(db_session)
        
        integration_data = CalendarIntegrationCreate(
            provider=CalendarProvider.APPLE,
            calendar_url="https://invalid-url.example.com/calendar",
            calendar_name="Test Calendar",
            username="test@example.com",
            password="test_password",
            sync_enabled=True,
        )
        
        # Devrait échouer car l'URL n'est pas accessible
        with pytest.raises(ValueError):
            service.create_integration(integration_data, test_user.id)

    def test_get_user_integrations_empty(self, db_session, test_user):
        """Test de récupération des intégrations quand il n'y en a aucune"""
        service = CalendarIntegrationService(db_session)
        integrations = service.get_user_integrations(test_user.id)
        assert len(integrations) == 0

    def test_get_integration_not_found(self, db_session, test_user):
        """Test de récupération d'une intégration qui n'existe pas"""
        service = CalendarIntegrationService(db_session)
        integration = service.get_integration(999, test_user.id)
        assert integration is None

    def test_update_integration_not_found(self, db_session, test_user):
        """Test de mise à jour d'une intégration qui n'existe pas"""
        service = CalendarIntegrationService(db_session)
        
        updates = CalendarIntegrationUpdate(
            calendar_name="Updated Name",
            sync_enabled=False,
        )
        
        result = service.update_integration(999, test_user.id, updates)
        assert result is None

    def test_delete_integration_not_found(self, db_session, test_user):
        """Test de suppression d'une intégration qui n'existe pas"""
        service = CalendarIntegrationService(db_session)
        result = service.delete_integration(999, test_user.id)
        assert result is False

    def test_sync_integration_not_found(self, db_session, test_user):
        """Test de synchronisation d'une intégration qui n'existe pas"""
        service = CalendarIntegrationService(db_session)
        result = service.sync_calendar(999, test_user.id)
        assert result.success is False
        assert "not found" in result.message.lower()

    def test_create_and_retrieve_integration_mock(self, db_session, test_user):
        """Test de création et récupération d'une intégration (sans validation CalDAV)"""
        # Créer directement l'intégration dans la base de données sans validation
        integration = CalendarIntegration(
            user_id=test_user.id,
            provider=CalendarProvider.APPLE.value,
            calendar_url="https://caldav.icloud.com/123456/calendars/test",
            calendar_name="Test Calendar",
            username="test@icloud.com",
            password="test-app-specific-password",
            sync_enabled=True,
            is_active=True,
        )
        db_session.add(integration)
        db_session.commit()
        db_session.refresh(integration)

        # Récupérer l'intégration
        service = CalendarIntegrationService(db_session)
        retrieved = service.get_integration(integration.id, test_user.id)
        
        assert retrieved is not None
        assert retrieved.id == integration.id
        assert retrieved.provider == CalendarProvider.APPLE.value
        assert retrieved.calendar_name == "Test Calendar"
        assert retrieved.username == "test@icloud.com"
        assert retrieved.sync_enabled is True
        assert retrieved.is_active is True

    def test_update_integration_mock(self, db_session, test_user):
        """Test de mise à jour d'une intégration"""
        # Créer une intégration de test
        integration = CalendarIntegration(
            user_id=test_user.id,
            provider=CalendarProvider.APPLE.value,
            calendar_url="https://caldav.icloud.com/123456/calendars/test",
            calendar_name="Original Name",
            username="test@icloud.com",
            password="test-password",
            sync_enabled=True,
            is_active=True,
        )
        db_session.add(integration)
        db_session.commit()
        db_session.refresh(integration)

        # Mettre à jour l'intégration
        service = CalendarIntegrationService(db_session)
        updates = CalendarIntegrationUpdate(
            calendar_name="Updated Name",
            sync_enabled=False,
        )
        
        updated = service.update_integration(integration.id, test_user.id, updates)
        
        assert updated is not None
        assert updated.calendar_name == "Updated Name"
        assert updated.sync_enabled is False
        assert updated.username == "test@icloud.com"  # Ne devrait pas changer

    def test_delete_integration_mock(self, db_session, test_user):
        """Test de suppression d'une intégration"""
        # Créer une intégration de test
        integration = CalendarIntegration(
            user_id=test_user.id,
            provider=CalendarProvider.APPLE.value,
            calendar_url="https://caldav.icloud.com/123456/calendars/test",
            calendar_name="Test Calendar",
            username="test@icloud.com",
            password="test-password",
            sync_enabled=True,
            is_active=True,
        )
        db_session.add(integration)
        db_session.commit()
        db_session.refresh(integration)

        # Supprimer l'intégration
        service = CalendarIntegrationService(db_session)
        result = service.delete_integration(integration.id, test_user.id)
        
        assert result is True
        
        # Vérifier que l'intégration a été supprimée
        retrieved = service.get_integration(integration.id, test_user.id)
        assert retrieved is None

    def test_get_multiple_user_integrations(self, db_session, test_user):
        """Test de récupération de plusieurs intégrations"""
        # Créer plusieurs intégrations
        integration1 = CalendarIntegration(
            user_id=test_user.id,
            provider=CalendarProvider.APPLE.value,
            calendar_url="https://caldav.icloud.com/123/calendars/1",
            calendar_name="Calendar 1",
            username="test1@icloud.com",
            password="password1",
        )
        integration2 = CalendarIntegration(
            user_id=test_user.id,
            provider=CalendarProvider.GOOGLE.value,
            calendar_url="https://calendar.google.com/calendar",
            calendar_name="Calendar 2",
            username="test2@gmail.com",
            password="password2",
        )
        db_session.add_all([integration1, integration2])
        db_session.commit()

        # Récupérer toutes les intégrations
        service = CalendarIntegrationService(db_session)
        integrations = service.get_user_integrations(test_user.id)
        
        assert len(integrations) == 2
        assert any(i.provider == CalendarProvider.APPLE.value for i in integrations)
        assert any(i.provider == CalendarProvider.GOOGLE.value for i in integrations)

    def test_sync_disabled_integration(self, db_session, test_user):
        """Test de synchronisation d'une intégration désactivée"""
        # Créer une intégration désactivée
        integration = CalendarIntegration(
            user_id=test_user.id,
            provider=CalendarProvider.APPLE.value,
            calendar_url="https://caldav.icloud.com/123456/calendars/test",
            calendar_name="Test Calendar",
            username="test@icloud.com",
            password="test-password",
            sync_enabled=False,
            is_active=True,
        )
        db_session.add(integration)
        db_session.commit()
        db_session.refresh(integration)

        # Tenter de synchroniser
        service = CalendarIntegrationService(db_session)
        result = service.sync_calendar(integration.id, test_user.id)
        
        assert result.success is False
        assert "disabled" in result.message.lower()
