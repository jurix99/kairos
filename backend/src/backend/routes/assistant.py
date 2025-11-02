"""
Routes API pour l'assistant IA
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..config.database import get_db
from ..config.auth import get_current_user
from ..models.database import User
from ..services.assistant_service import AssistantService, ExtractedEvent, AssistantResponse


router = APIRouter(prefix="/assistant", tags=["assistant"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Modèle pour une requête de chat"""
    message: str
    conversation_history: List[Dict[str, str]] = []


class ChatResponse(BaseModel):
    """Modèle pour la réponse de chat"""
    message: str
    events: List[ExtractedEvent] = []
    action: str = "chat"


class CreateEventsRequest(BaseModel):
    """Modèle pour créer des événements depuis l'assistant"""
    events: List[ExtractedEvent]


class CreateEventsResponse(BaseModel):
    """Modèle pour la réponse de création d'événements"""
    success: bool
    created_event_ids: List[int]
    message: str


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Discuter avec l'assistant IA
    """
    logger.info(f"Requête chat reçue de l'utilisateur {current_user.id}")
    logger.debug(f"Message: {request.message[:100]}...")
    logger.debug(f"Historique: {len(request.conversation_history)} messages")
    
    try:
        logger.debug("Initialisation du service Assistant")
        service = AssistantService(db)
        
        logger.info("Appel du service chat")
        response = await service.chat(
            message=request.message,
            user_id=current_user.id,
            conversation_history=request.conversation_history
        )
        
        logger.info(f"Réponse reçue du service: action={response.action}, events={len(response.events)}")
        
        chat_response = ChatResponse(
            message=response.message,
            events=response.events,
            action=response.action
        )
        
        logger.info("Réponse envoyée avec succès")
        return chat_response
        
    except Exception as e:
        logger.error(f"Erreur dans chat_with_assistant: {e}")
        logger.error(f"Type d'erreur: {type(e).__name__}")
        logger.exception("Stack trace complète:")
        
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du traitement du message: {str(e)}"
        )


@router.post("/create-events", response_model=CreateEventsResponse)
async def create_events_from_assistant(
    request: CreateEventsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer des événements à partir des données extraites par l'assistant
    """
    logger.info(f"Requête création d'événements de l'utilisateur {current_user.id}")
    logger.debug(f"Nombre d'événements à créer: {len(request.events)}")
    
    try:
        service = AssistantService(db)
        created_event_ids = await service.create_events_from_extracted(
            events=request.events,
            user_id=current_user.id
        )
        
        success = len(created_event_ids) > 0
        message = f"{len(created_event_ids)} événement(s) créé(s) avec succès!" if success else "Aucun événement n'a pu être créé."
        
        logger.info(f"Création terminée: {len(created_event_ids)} événements créés")
        
        return CreateEventsResponse(
            success=success,
            created_event_ids=created_event_ids,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Erreur dans create_events_from_assistant: {e}")
        logger.exception("Stack trace:")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la création des événements: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Vérifier l'état de l'assistant
    """
    logger.debug("Health check de l'assistant")
    return {"status": "healthy", "service": "assistant"}
