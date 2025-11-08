"""
Service pour gérer les intégrations avec des calendriers externes (Apple Calendar, Google Calendar, etc.)
"""

import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from caldav import DAVClient
from icalendar import Calendar, Event as ICalEvent
import pytz

from ..models.database import CalendarIntegration, Event, Category
from ..models.schemas import (
    CalendarIntegrationCreate,
    CalendarIntegrationUpdate,
    CalendarIntegrationResponse,
    SyncResult,
    CalendarProvider,
    EventCreate,
    PriorityLevel,
    EventStatus,
)

logger = logging.getLogger(__name__)


class CalendarIntegrationService:
    """Service pour gérer les intégrations de calendrier"""

    def __init__(self, db: Session):
        self.db = db

    def create_integration(
        self, integration: CalendarIntegrationCreate, user_id: int
    ) -> CalendarIntegration:
        """Créer une nouvelle intégration de calendrier"""
        # Valider la connexion avant de créer l'intégration
        if integration.provider == CalendarProvider.APPLE:
            # Test de connexion CalDAV
            try:
                self._test_caldav_connection(
                    integration.calendar_url, integration.username, integration.password
                )
            except Exception as e:
                logger.error(f"Failed to connect to CalDAV server: {e}")
                raise ValueError(f"Cannot connect to calendar: {str(e)}")

        db_integration = CalendarIntegration(
            user_id=user_id,
            provider=integration.provider.value,
            calendar_url=integration.calendar_url,
            calendar_name=integration.calendar_name,
            username=integration.username,
            password=integration.password,  # TODO: Encrypt password
            sync_enabled=integration.sync_enabled,
            is_active=True,
        )
        self.db.add(db_integration)
        self.db.commit()
        self.db.refresh(db_integration)
        logger.info(f"Created calendar integration {db_integration.id} for user {user_id}")
        return db_integration

    def get_integration(
        self, integration_id: int, user_id: int
    ) -> Optional[CalendarIntegration]:
        """Récupérer une intégration par ID"""
        return (
            self.db.query(CalendarIntegration)
            .filter(
                CalendarIntegration.id == integration_id,
                CalendarIntegration.user_id == user_id,
            )
            .first()
        )

    def get_user_integrations(self, user_id: int) -> List[CalendarIntegration]:
        """Récupérer toutes les intégrations d'un utilisateur"""
        return (
            self.db.query(CalendarIntegration)
            .filter(CalendarIntegration.user_id == user_id)
            .all()
        )

    def update_integration(
        self, integration_id: int, user_id: int, updates: CalendarIntegrationUpdate
    ) -> Optional[CalendarIntegration]:
        """Mettre à jour une intégration"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(integration, key, value)

        integration.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(integration)
        logger.info(f"Updated calendar integration {integration_id}")
        return integration

    def delete_integration(self, integration_id: int, user_id: int) -> bool:
        """Supprimer une intégration"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return False

        self.db.delete(integration)
        self.db.commit()
        logger.info(f"Deleted calendar integration {integration_id}")
        return True

    def sync_calendar(self, integration_id: int, user_id: int) -> SyncResult:
        """Synchroniser les événements avec le calendrier externe"""
        integration = self.get_integration(integration_id, user_id)
        if not integration:
            return SyncResult(
                success=False,
                message="Integration not found",
                errors=["Integration not found"],
            )

        if not integration.is_active or not integration.sync_enabled:
            return SyncResult(
                success=False,
                message="Integration is disabled",
                errors=["Integration is disabled"],
            )

        try:
            if integration.provider == CalendarProvider.APPLE.value:
                result = self._sync_caldav_calendar(integration, user_id)
            else:
                result = SyncResult(
                    success=False,
                    message=f"Provider {integration.provider} not yet supported",
                    errors=[f"Provider {integration.provider} not implemented"],
                )

            if result.success:
                integration.last_sync = datetime.utcnow()
                self.db.commit()

            return result
        except Exception as e:
            logger.error(f"Error syncing calendar {integration_id}: {e}")
            return SyncResult(
                success=False,
                message=f"Sync failed: {str(e)}",
                errors=[str(e)],
            )

    def _test_caldav_connection(
        self, calendar_url: str, username: Optional[str], password: str
    ) -> None:
        """Tester la connexion à un serveur CalDAV"""
        try:
            client = DAVClient(
                url=calendar_url,
                username=username,
                password=password,
            )
            principal = client.principal()
            # Test if we can access calendars
            calendars = principal.calendars()
            logger.info(f"Successfully connected to CalDAV server, found {len(calendars)} calendars")
        except Exception as e:
            logger.error(f"CalDAV connection test failed: {e}")
            raise

    def _sync_caldav_calendar(
        self, integration: CalendarIntegration, user_id: int
    ) -> SyncResult:
        """Synchroniser avec un calendrier CalDAV (Apple Calendar, etc.)"""
        events_imported = 0
        events_exported = 0
        errors = []

        try:
            # Connexion au serveur CalDAV
            client = DAVClient(
                url=integration.calendar_url,
                username=integration.username,
                password=integration.password,
            )
            principal = client.principal()
            calendars = principal.calendars()

            if not calendars:
                return SyncResult(
                    success=False,
                    message="No calendars found",
                    errors=["No calendars found on the server"],
                )

            # Utiliser le premier calendrier disponible
            calendar = calendars[0]

            # Import des événements depuis le calendrier externe
            # Récupérer les événements des 30 derniers jours et 90 prochains jours
            from datetime import timedelta

            start_date = datetime.utcnow() - timedelta(days=30)
            end_date = datetime.utcnow() + timedelta(days=90)

            # Récupérer les événements du calendrier
            events = calendar.date_search(start=start_date, end=end_date, expand=True)

            # Obtenir la catégorie par défaut pour l'utilisateur
            default_category = (
                self.db.query(Category)
                .filter(Category.user_id == user_id)
                .first()
            )

            if not default_category:
                # Créer une catégorie par défaut si elle n'existe pas
                default_category = Category(
                    name="Imported",
                    color_code="#6B7280",
                    description="Events imported from external calendars",
                    user_id=user_id,
                )
                self.db.add(default_category)
                self.db.commit()
                self.db.refresh(default_category)

            # Importer les événements
            for cal_event in events:
                try:
                    # Parser l'événement iCal
                    ical = Calendar.from_ical(cal_event.data)
                    for component in ical.walk():
                        if component.name == "VEVENT":
                            # Extraire les informations de l'événement
                            title = str(component.get("summary", "Untitled Event"))
                            description = str(component.get("description", ""))
                            start_time = component.get("dtstart").dt
                            end_time = component.get("dtend").dt
                            location = str(component.get("location", ""))

                            # Convertir en datetime si c'est une date
                            if not isinstance(start_time, datetime):
                                start_time = datetime.combine(
                                    start_time, datetime.min.time()
                                )
                            if not isinstance(end_time, datetime):
                                end_time = datetime.combine(
                                    end_time, datetime.min.time()
                                )

                            # Assurer que les datetimes sont timezone-aware
                            if start_time.tzinfo is None:
                                start_time = pytz.utc.localize(start_time)
                            if end_time.tzinfo is None:
                                end_time = pytz.utc.localize(end_time)

                            # Convertir en UTC
                            start_time = start_time.astimezone(pytz.utc).replace(
                                tzinfo=None
                            )
                            end_time = end_time.astimezone(pytz.utc).replace(
                                tzinfo=None
                            )

                            # Vérifier si l'événement existe déjà
                            existing_event = (
                                self.db.query(Event)
                                .filter(
                                    Event.user_id == user_id,
                                    Event.title == title,
                                    Event.start_time == start_time,
                                )
                                .first()
                            )

                            if not existing_event:
                                # Créer un nouvel événement
                                new_event = Event(
                                    user_id=user_id,
                                    title=title,
                                    description=description,
                                    start_time=start_time,
                                    end_time=end_time,
                                    location=location,
                                    category_id=default_category.id,
                                    priority=PriorityLevel.MEDIUM.value,
                                    status=EventStatus.PENDING.value,
                                    is_flexible=False,  # Les événements importés ne sont pas flexibles
                                )
                                self.db.add(new_event)
                                events_imported += 1

                except Exception as e:
                    error_msg = f"Error importing event: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Commit tous les nouveaux événements
            self.db.commit()

            return SyncResult(
                success=True,
                events_imported=events_imported,
                events_exported=events_exported,
                errors=errors,
                message=f"Successfully synced {events_imported} events from calendar",
            )

        except Exception as e:
            logger.error(f"Error in CalDAV sync: {e}")
            return SyncResult(
                success=False,
                message=f"Sync failed: {str(e)}",
                errors=[str(e)],
            )
