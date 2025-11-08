"""
Routes API pour la gestion des intégrations de calendrier externes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..config.auth import get_current_user
from ..models.database import User
from ..models.schemas import (
    CalendarIntegrationCreate,
    CalendarIntegrationUpdate,
    CalendarIntegrationResponse,
    SyncResult,
)
from ..services.calendar_integration_service import CalendarIntegrationService

router = APIRouter(prefix="/integrations", tags=["calendar-integrations"])


@router.post("/", response_model=CalendarIntegrationResponse)
async def create_integration(
    integration: CalendarIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Créer une nouvelle intégration de calendrier externe"""
    service = CalendarIntegrationService(db)
    try:
        db_integration = service.create_integration(integration, current_user.id)
        return db_integration
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating integration: {str(e)}")


@router.get("/", response_model=List[CalendarIntegrationResponse])
async def get_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupérer toutes les intégrations de calendrier de l'utilisateur"""
    service = CalendarIntegrationService(db)
    return service.get_user_integrations(current_user.id)


@router.get("/{integration_id}", response_model=CalendarIntegrationResponse)
async def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupérer une intégration de calendrier par ID"""
    service = CalendarIntegrationService(db)
    integration = service.get_integration(integration_id, current_user.id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.put("/{integration_id}", response_model=CalendarIntegrationResponse)
async def update_integration(
    integration_id: int,
    updates: CalendarIntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mettre à jour une intégration de calendrier"""
    service = CalendarIntegrationService(db)
    integration = service.update_integration(integration_id, current_user.id, updates)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Supprimer une intégration de calendrier"""
    service = CalendarIntegrationService(db)
    success = service.delete_integration(integration_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Integration not found")
    return {"message": "Integration deleted successfully"}


@router.post("/{integration_id}/sync", response_model=SyncResult)
async def sync_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Synchroniser les événements avec le calendrier externe"""
    service = CalendarIntegrationService(db)
    result = service.sync_calendar(integration_id, current_user.id)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return result
