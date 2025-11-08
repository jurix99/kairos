"""
Routes API pour le système d'orchestration multi-agents
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..config.database import get_db
from ..config.auth import get_current_user
from ..models.schemas import (
    NeedClassificationRequest,
    NeedClassificationResponse,
    AgentTaskRequest,
    AgentTaskResponse,
    OrchestratedPlanRequest,
    OrchestratedPlanResponse,
    AgentType,
    NeedType
)
from ..services.orchestration_service import OrchestrationService
from ..services.need_classifier_service import NeedClassifierService
from ..services.multi_agent_orchestrator_service import MultiAgentOrchestratorService
from ..models.database import User

router = APIRouter(prefix="/api/orchestration", tags=["orchestration"])


@router.post("/classify", response_model=NeedClassificationResponse)
async def classify_need(
    request: NeedClassificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Classifie un besoin utilisateur (Niveau 1)
    
    Identifie le type de besoin et suggère les agents appropriés
    """
    classifier = NeedClassifierService(db)
    return await classifier.classify_need(request)


@router.post("/agent/execute", response_model=AgentTaskResponse)
async def execute_agent_task(
    request: AgentTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exécute une tâche avec un agent spécifique (Niveau 2)
    
    Permet d'invoquer manuellement un agent particulier
    """
    orchestrator = MultiAgentOrchestratorService(db)
    return await orchestrator.execute_agent_task(request, current_user.id)


@router.post("/plan", response_model=OrchestratedPlanResponse)
async def create_orchestrated_plan(
    request: OrchestratedPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crée un plan orchestré complet
    
    Combine classification + exécution des agents + intégration
    C'est le point d'entrée principal pour les utilisateurs
    """
    orchestration_service = OrchestrationService(db)
    return await orchestration_service.create_orchestrated_plan(request, current_user.id)


@router.get("/agents", response_model=List[dict])
async def list_available_agents():
    """
    Liste tous les agents disponibles avec leurs descriptions
    """
    agents = [
        {
            "type": AgentType.EXECUTIVE.value,
            "name": "Agent Exécutif",
            "description": "Génère des tâches actionables pour des besoins simples et ponctuels",
            "use_cases": ["Réserver un restaurant", "Acheter un cadeau", "Appeler quelqu'un"]
        },
        {
            "type": AgentType.COACH.value,
            "name": "Agent Coach",
            "description": "Crée des plans progressifs pour développer des habitudes et compétences",
            "use_cases": ["Courir un marathon", "Apprendre une langue", "Méditer quotidiennement"]
        },
        {
            "type": AgentType.STRATEGIST.value,
            "name": "Agent Stratège",
            "description": "Définit les grandes phases d'un projet complexe",
            "use_cases": ["Créer une entreprise", "Lancer un produit", "Rénover une maison"]
        },
        {
            "type": AgentType.PLANNER.value,
            "name": "Agent Planificateur",
            "description": "Crée des plannings détaillés avec durées et dépendances",
            "use_cases": ["Planifier un projet", "Organiser un voyage", "Préparer un examen"]
        },
        {
            "type": AgentType.RESOURCE.value,
            "name": "Agent Ressources",
            "description": "Identifie les ressources nécessaires (budget, outils, compétences)",
            "use_cases": ["Budgétiser un projet", "Identifier les outils nécessaires", "Évaluer les compétences"]
        },
        {
            "type": AgentType.RESEARCH.value,
            "name": "Agent Recherche",
            "description": "Compare des options et synthétise des informations pour la prise de décision",
            "use_cases": ["Choisir une assurance", "Comparer des fournisseurs", "Sélectionner un outil"]
        },
        {
            "type": AgentType.SOCIAL.value,
            "name": "Agent Social",
            "description": "Planifie et coordonne des événements sociaux",
            "use_cases": ["Organiser un mariage", "Planifier une fête", "Coordonner une réunion"]
        }
    ]
    
    return agents


@router.get("/need-types", response_model=List[dict])
async def list_need_types():
    """
    Liste tous les types de besoins reconnus par le système
    """
    need_types = [
        {
            "type": NeedType.PUNCTUAL_TASK.value,
            "name": "Tâche Ponctuelle",
            "description": "Action simple et court terme",
            "characteristics": ["Court terme", "Actions simples", "Objectif unique"],
            "examples": ["Réserver un restaurant", "Acheter un cadeau", "Envoyer un email"],
            "agents": [AgentType.EXECUTIVE.value]
        },
        {
            "type": NeedType.HABIT_SKILL.value,
            "name": "Habitude/Compétence",
            "description": "Développement long terme avec répétition et progression",
            "characteristics": ["Long terme", "Répétition", "Progression graduelle"],
            "examples": ["Courir un marathon", "Apprendre une langue", "Méditer quotidiennement"],
            "agents": [AgentType.COACH.value, AgentType.PLANNER.value]
        },
        {
            "type": NeedType.COMPLEX_PROJECT.value,
            "name": "Projet Complexe",
            "description": "Projet multi-étapes avec dépendances et ressources",
            "characteristics": ["Multi-étapes", "Dépendances", "Ressources variées"],
            "examples": ["Créer une entreprise", "Développer une application", "Rénover une maison"],
            "agents": [
                AgentType.STRATEGIST.value,
                AgentType.PLANNER.value,
                AgentType.RESOURCE.value,
                AgentType.EXECUTIVE.value
            ]
        },
        {
            "type": NeedType.DECISION_RESEARCH.value,
            "name": "Décision/Recherche",
            "description": "Comparaison et analyse pour prise de décision",
            "characteristics": ["Comparaison", "Critères multiples", "Analyse approfondie"],
            "examples": ["Choisir une assurance", "Comparer des voitures", "Sélectionner un fournisseur"],
            "agents": [AgentType.RESEARCH.value]
        },
        {
            "type": NeedType.SOCIAL_EVENT.value,
            "name": "Événement Social",
            "description": "Organisation d'événement avec logistique et invités",
            "characteristics": ["Logistique", "Coordination", "Gestion des invités", "Budget"],
            "examples": ["Organiser un mariage", "Planifier une fête d'anniversaire", "Coordonner une réunion"],
            "agents": [AgentType.SOCIAL.value, AgentType.PLANNER.value]
        }
    ]
    
    return need_types


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Vérifie que le système d'orchestration fonctionne
    """
    try:
        # Vérifier la connexion DB
        db.execute("SELECT 1")
        
        # Vérifier si OpenAI est configuré
        from ..config.settings import settings
        openai_available = bool(settings.OPENAI_API_KEY)
        
        return {
            "status": "healthy",
            "database": "connected",
            "openai": "available" if openai_available else "not configured (fallback mode)",
            "agents_available": len(AgentType),
            "need_types_supported": len(NeedType)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service health check failed: {str(e)}"
        )
