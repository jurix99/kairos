"""
Routes API pour le scheduling automatique
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.schemas import EventCreate, SchedulingResult, ConflictSuggestion
from ..services.scheduler_service import SchedulerService
from ..services.event_service import EventService

router = APIRouter(prefix="/schedule", tags=["scheduling"])


@router.post("/auto", response_model=SchedulingResult)
async def schedule_event(event: EventCreate, db: Session = Depends(get_db)):
    """Planifier automatiquement un événement"""
    # Vérifier que la catégorie existe
    event_service = EventService(db)
    from ..models.database import Category
    category = db.query(Category).filter(Category.id == event.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée")
    
    scheduler = SchedulerService(db)
    duration = timedelta(minutes=event.duration_minutes)
    
    result = scheduler.find_available_slot(
        duration=duration,
        preferred_start=event.start_time,
        priority=event.priority,
        category_id=event.category_id
    )
    
    # Si un créneau est trouvé, créer l'événement
    if result.success and result.scheduled_time:
        # Mettre à jour l'heure de début avec le créneau trouvé
        event.start_time = result.scheduled_time
        created_event = event_service.create_event(event)
        
        # Ajouter l'ID de l'événement créé au résultat
        result.message += f" - Événement créé avec l'ID {created_event.id}"
    
    return result


@router.get("/daily")
async def get_daily_schedule(
    date: datetime = Query(..., description="Date pour le planning quotidien"),
    db: Session = Depends(get_db)
):
    """Récupérer le planning d'une journée"""
    scheduler = SchedulerService(db)
    events = scheduler.get_daily_schedule(date)
    return {"date": date.date(), "events": events}


@router.get("/weekly")
async def get_weekly_schedule(
    start_date: datetime = Query(..., description="Date de début de la semaine"),
    db: Session = Depends(get_db)
):
    """Récupérer le planning d'une semaine"""
    scheduler = SchedulerService(db)
    schedule = scheduler.get_weekly_schedule(start_date)
    return {"start_date": start_date.date(), "schedule": schedule}


@router.post("/conflicts/resolve")
async def resolve_conflict(suggestion: ConflictSuggestion, db: Session = Depends(get_db)):
    """Appliquer une suggestion de résolution de conflit"""
    scheduler = SchedulerService(db)
    success = scheduler.apply_conflict_resolution(suggestion)
    
    if success:
        return {"message": "Conflit résolu avec succès"}
    else:
        raise HTTPException(status_code=400, detail="Impossible de résoudre le conflit")


@router.get("/conflicts/check")
async def check_conflicts(
    start_time: datetime = Query(..., description="Heure de début"),
    duration_minutes: int = Query(..., description="Durée en minutes"),
    db: Session = Depends(get_db)
):
    """Vérifier les conflits pour un créneau donné"""
    scheduler = SchedulerService(db)
    end_time = start_time + timedelta(minutes=duration_minutes)
    conflicts = scheduler._check_conflicts(start_time, end_time)
    
    return {
        "start_time": start_time,
        "end_time": end_time,
        "has_conflicts": len(conflicts) > 0,
        "conflicts_count": len(conflicts),
        "conflicting_events": [
            {
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "is_flexible": event.is_flexible,
                "priority": event.priority
            }
            for event in conflicts
        ]
    }


@router.get("/availability")
async def get_availability(
    date: datetime = Query(..., description="Date à vérifier"),
    working_hours_start: int = Query(8, description="Heure de début (0-23)"),
    working_hours_end: int = Query(20, description="Heure de fin (0-23)"),
    slot_duration: int = Query(30, description="Durée des créneaux en minutes"),
    db: Session = Depends(get_db)
):
    """Récupérer les créneaux disponibles pour une journée"""
    scheduler = SchedulerService(db)
    
    # Créer les créneaux de la journée
    start_of_day = datetime.combine(date.date(), datetime.min.time()).replace(
        hour=working_hours_start, minute=0
    )
    end_of_day = datetime.combine(date.date(), datetime.min.time()).replace(
        hour=working_hours_end, minute=0
    )
    
    available_slots = []
    current_time = start_of_day
    slot_duration_td = timedelta(minutes=slot_duration)
    
    while current_time + slot_duration_td <= end_of_day:
        conflicts = scheduler._check_conflicts(current_time, current_time + slot_duration_td)
        
        if not conflicts:
            available_slots.append({
                "start_time": current_time,
                "end_time": current_time + slot_duration_td,
                "duration_minutes": slot_duration
            })
        
        current_time += slot_duration_td
    
    return {
        "date": date.date(),
        "working_hours": {
            "start": working_hours_start,
            "end": working_hours_end
        },
        "slot_duration_minutes": slot_duration,
        "total_slots": len(available_slots),
        "available_slots": available_slots
    } 