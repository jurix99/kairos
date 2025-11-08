"""
Routes API pour le scheduling intelligent avec optimisation géographique
"""

from datetime import datetime, timedelta, time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..config.database import get_db
from ..models.schemas import PriorityLevel
from ..services.smart_scheduler_service import (
    SmartSchedulerService,
    TimeConstraint,
    SmartSchedulingResult
)
from ..services.travel_service import TravelService


router = APIRouter(prefix="/smart-schedule", tags=["smart-scheduling"])


class SmartScheduleRequest(BaseModel):
    """Requête pour le scheduling intelligent"""
    user_id: int
    duration_minutes: int = Field(..., gt=0, le=1440)
    preferred_start: datetime
    priority: PriorityLevel = PriorityLevel.MEDIUM
    location: Optional[str] = None
    category_id: Optional[int] = None
    
    # Contraintes horaires
    not_before: Optional[str] = Field(None, description="Heure minimale (HH:MM)")
    not_after: Optional[str] = Field(None, description="Heure maximale (HH:MM)")
    morning_only: bool = False
    afternoon_only: bool = False
    evening_only: bool = False
    
    search_days: int = Field(7, ge=1, le=30)


class TravelConflictCheck(BaseModel):
    """Requête pour vérifier les conflits de déplacement"""
    user_id: int
    date: datetime


class OptimizeSequenceRequest(BaseModel):
    """Requête pour optimiser une séquence d'événements"""
    user_id: int
    date: datetime
    minimize_travel: bool = True


class TravelTimeRequest(BaseModel):
    """Requête pour calculer un temps de trajet"""
    origin: str
    destination: str


@router.post("/find-best-slot")
async def find_best_slot(
    request: SmartScheduleRequest,
    db: Session = Depends(get_db)
):
    """
    Trouve le meilleur créneau pour un événement en tenant compte de:
    - Disponibilité
    - Lieu et temps de trajet
    - Priorité
    - Durée
    - Contraintes horaires personnalisées
    """
    try:
        # Construire les contraintes de temps
        constraints = TimeConstraint(
            not_before=time.fromisoformat(request.not_before) if request.not_before else None,
            not_after=time.fromisoformat(request.not_after) if request.not_after else None,
            morning_only=request.morning_only,
            afternoon_only=request.afternoon_only,
            evening_only=request.evening_only
        )
        
        scheduler = SmartSchedulerService(db)
        result = scheduler.find_best_slot(
            user_id=request.user_id,
            duration=timedelta(minutes=request.duration_minutes),
            preferred_start=request.preferred_start,
            priority=request.priority,
            location=request.location,
            category_id=request.category_id,
            constraints=constraints,
            search_days=request.search_days
        )
        
        return {
            "success": result.success,
            "scheduled_time": result.scheduled_time.isoformat() if result.scheduled_time else None,
            "message": result.message,
            "travel_warnings": result.travel_warnings,
            "conflicts": result.conflicts,
            "optimization_applied": result.optimization_applied
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erreur de validation: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")


@router.post("/detect-travel-conflicts")
async def detect_travel_conflicts(
    request: TravelConflictCheck,
    db: Session = Depends(get_db)
):
    """
    Détecte les conflits logistiques dus aux temps de trajet pour une journée
    et propose des réorganisations fluides.
    
    Exemple de réponse:
    "Ton trajet entre A et B prend 40 min, veux-tu que je déplace ta tâche suivante à 15h45 ?"
    """
    scheduler = SmartSchedulerService(db)
    conflicts = scheduler.detect_travel_conflicts(request.user_id, request.date)
    
    return {
        "date": request.date.date().isoformat(),
        "conflicts_found": len(conflicts),
        "conflicts": conflicts,
        "message": (
            f"{len(conflicts)} conflit(s) de déplacement détecté(s)"
            if conflicts else "Aucun conflit de déplacement détecté"
        )
    }


@router.post("/optimize-sequence")
async def optimize_sequence(
    request: OptimizeSequenceRequest,
    db: Session = Depends(get_db)
):
    """
    Optimise l'enchaînement des événements d'une journée pour:
    - Grouper les événements proches géographiquement
    - Minimiser les déplacements
    """
    scheduler = SmartSchedulerService(db)
    result = scheduler.optimize_event_sequence(
        user_id=request.user_id,
        date=request.date,
        minimize_travel=request.minimize_travel
    )
    
    return result


@router.post("/calculate-travel-time")
async def calculate_travel_time(request: TravelTimeRequest):
    """
    Calcule le temps de trajet estimé entre deux lieux
    """
    travel_service = TravelService()
    travel_info = travel_service.get_travel_info(request.origin, request.destination)
    
    return travel_info


@router.get("/travel-analysis/{user_id}")
async def analyze_daily_travel(
    user_id: int,
    date: datetime = Query(..., description="Date à analyser"),
    db: Session = Depends(get_db)
):
    """
    Analyse complète des déplacements d'une journée avec statistiques
    """
    scheduler = SmartSchedulerService(db)
    
    # Récupérer les événements du jour
    events = scheduler._get_day_events(user_id, date)
    
    if not events:
        return {
            "date": date.date().isoformat(),
            "total_events": 0,
            "message": "Aucun événement planifié pour cette journée"
        }
    
    # Calculer les temps de trajet
    total_travel_time = timedelta(0)
    travel_details = []
    
    for i in range(len(events) - 1):
        current = events[i]
        next_event = events[i + 1]
        
        if current.location and next_event.location:
            travel_time = TravelService.calculate_travel_time(
                current.location, next_event.location
            )
            total_travel_time += travel_time
            
            travel_details.append({
                "from_event": {
                    "id": current.id,
                    "title": current.title,
                    "location": current.location,
                    "end_time": current.end_time.isoformat()
                },
                "to_event": {
                    "id": next_event.id,
                    "title": next_event.title,
                    "location": next_event.location,
                    "start_time": next_event.start_time.isoformat()
                },
                "travel_time_minutes": int(travel_time.total_seconds() / 60),
                "available_time_minutes": int(
                    (next_event.start_time - current.end_time).total_seconds() / 60
                ),
                "is_sufficient": travel_time <= (next_event.start_time - current.end_time)
            })
    
    # Grouper par lieu
    locations = {}
    for event in events:
        if event.location:
            loc = event.location
            if loc not in locations:
                locations[loc] = []
            locations[loc].append({
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat()
            })
    
    return {
        "date": date.date().isoformat(),
        "total_events": len(events),
        "events_with_location": sum(1 for e in events if e.location),
        "total_travel_minutes": int(total_travel_time.total_seconds() / 60),
        "travel_details": travel_details,
        "locations_visited": len(locations),
        "location_groups": locations,
        "recommendations": _generate_travel_recommendations(travel_details)
    }


def _generate_travel_recommendations(travel_details: List[dict]) -> List[str]:
    """Génère des recommandations basées sur l'analyse des déplacements"""
    recommendations = []
    
    # Vérifier les temps de trajet insuffisants
    insufficient = [t for t in travel_details if not t["is_sufficient"]]
    if insufficient:
        recommendations.append(
            f"⚠️ {len(insufficient)} déplacement(s) avec temps insuffisant détecté(s). "
            "Considérez réorganiser ces événements."
        )
    
    # Vérifier les déplacements longs
    long_travels = [t for t in travel_details if t["travel_time_minutes"] > 45]
    if long_travels:
        recommendations.append(
            f"🚗 {len(long_travels)} déplacement(s) de plus de 45 min. "
            "Essayez de grouper les événements par zone géographique."
        )
    
    # Calculer le temps total de déplacement
    total_travel = sum(t["travel_time_minutes"] for t in travel_details)
    if total_travel > 120:
        recommendations.append(
            f"⏱️ Temps de déplacement total: {total_travel} min. "
            "Une réorganisation pourrait économiser du temps."
        )
    
    if not recommendations:
        recommendations.append("✅ Votre organisation actuelle est optimale !")
    
    return recommendations


@router.post("/constraints/validate")
async def validate_time_constraints(
    not_before: Optional[str] = Body(None, description="Heure minimale (HH:MM)"),
    not_after: Optional[str] = Body(None, description="Heure maximale (HH:MM)"),
    morning_only: bool = Body(False),
    afternoon_only: bool = Body(False),
    evening_only: bool = Body(False),
    test_time: datetime = Body(..., description="Heure à tester")
):
    """
    Valide si une heure donnée satisfait des contraintes horaires
    """
    try:
        constraints = TimeConstraint(
            not_before=time.fromisoformat(not_before) if not_before else None,
            not_after=time.fromisoformat(not_after) if not_after else None,
            morning_only=morning_only,
            afternoon_only=afternoon_only,
            evening_only=evening_only
        )
        
        is_valid = constraints.is_valid_time(test_time)
        
        reasons = []
        if not is_valid:
            if morning_only and not (6 <= test_time.hour < 12):
                reasons.append("Doit être le matin (6h-12h)")
            if afternoon_only and not (12 <= test_time.hour < 18):
                reasons.append("Doit être l'après-midi (12h-18h)")
            if evening_only and not (18 <= test_time.hour < 22):
                reasons.append("Doit être le soir (18h-22h)")
            if not_before and test_time.time() < not_before:
                reasons.append(f"Ne peut pas être avant {not_before}")
            if not_after and test_time.time() > not_after:
                reasons.append(f"Ne peut pas être après {not_after}")
        
        return {
            "test_time": test_time.isoformat(),
            "is_valid": is_valid,
            "reasons": reasons if not is_valid else ["Toutes les contraintes sont satisfaites"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erreur de validation: {str(e)}")
