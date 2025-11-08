"""
Tests pour le système d'orchestration multi-agents
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.database import Base, User, Category, Goal
from backend.models.schemas import (
    NeedType,
    NeedComplexity,
    AgentType,
    NeedClassificationRequest,
    AgentTaskRequest,
    OrchestratedPlanRequest
)
from backend.services.need_classifier_service import NeedClassifierService
from backend.services.multi_agent_orchestrator_service import MultiAgentOrchestratorService
from backend.services.orchestration_service import OrchestrationService


# Configuration de la base de données de test
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Crée une session de base de données pour les tests"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    
    # Créer un utilisateur de test
    user = User(
        external_id="test_user_123",
        name="Test User",
        email="test@example.com",
        provider="test"
    )
    session.add(user)
    
    # Créer une catégorie de test
    category = Category(
        name="Test Category",
        color_code="#FF0000",
        user_id=None  # Catégorie par défaut
    )
    session.add(category)
    
    session.commit()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Récupère l'utilisateur de test"""
    return db_session.query(User).first()


# Tests pour NeedClassifierService

def test_classify_punctual_task(db_session):
    """Test de classification d'une tâche ponctuelle"""
    classifier = NeedClassifierService(db_session)
    
    request = NeedClassificationRequest(
        user_input="Je veux réserver un restaurant pour ce soir"
    )
    
    result = classifier._classify_with_keywords(request)
    
    assert result.need_type == NeedType.PUNCTUAL_TASK
    assert AgentType.EXECUTIVE in result.suggested_agents
    assert result.confidence > 0


def test_classify_habit_skill(db_session):
    """Test de classification d'une habitude/compétence"""
    classifier = NeedClassifierService(db_session)
    
    request = NeedClassificationRequest(
        user_input="Je veux apprendre à courir un marathon en 6 mois"
    )
    
    result = classifier._classify_with_keywords(request)
    
    assert result.need_type == NeedType.HABIT_SKILL
    assert AgentType.COACH in result.suggested_agents
    assert result.confidence > 0


def test_classify_complex_project(db_session):
    """Test de classification d'un projet complexe"""
    classifier = NeedClassifierService(db_session)
    
    request = NeedClassificationRequest(
        user_input="Je veux créer une entreprise de développement web avec plusieurs phases de développement"
    )
    
    result = classifier._classify_with_keywords(request)
    
    assert result.need_type == NeedType.COMPLEX_PROJECT
    assert AgentType.STRATEGIST in result.suggested_agents
    assert AgentType.PLANNER in result.suggested_agents
    assert result.complexity in [NeedComplexity.COMPLEX, NeedComplexity.VERY_COMPLEX]


def test_classify_decision_research(db_session):
    """Test de classification d'une décision/recherche"""
    classifier = NeedClassifierService(db_session)
    
    request = NeedClassificationRequest(
        user_input="Je veux choisir la meilleure assurance auto en comparant les options"
    )
    
    result = classifier._classify_with_keywords(request)
    
    assert result.need_type == NeedType.DECISION_RESEARCH
    assert AgentType.RESEARCH in result.suggested_agents


def test_classify_social_event(db_session):
    """Test de classification d'un événement social"""
    classifier = NeedClassifierService(db_session)
    
    request = NeedClassificationRequest(
        user_input="Je veux organiser un mariage avec 100 invités"
    )
    
    result = classifier._classify_with_keywords(request)
    
    assert result.need_type == NeedType.SOCIAL_EVENT
    assert AgentType.SOCIAL in result.suggested_agents


def test_complexity_estimation(db_session):
    """Test de l'estimation de complexité"""
    classifier = NeedClassifierService(db_session)
    
    # Simple
    simple_text = "acheter du pain"
    assert classifier._estimate_complexity(simple_text) == NeedComplexity.SIMPLE
    
    # Complexe
    complex_text = "créer un projet avec plusieurs phases et étapes sur plusieurs mois"
    result = classifier._estimate_complexity(complex_text)
    assert result in [NeedComplexity.COMPLEX, NeedComplexity.VERY_COMPLEX]


# Tests pour MultiAgentOrchestratorService

@pytest.mark.asyncio
async def test_coach_agent_fallback(db_session, test_user):
    """Test de l'agent Coach en mode fallback"""
    orchestrator = MultiAgentOrchestratorService(db_session)
    
    request = AgentTaskRequest(
        agent_type=AgentType.COACH,
        user_input="Apprendre le piano",
        need_type=NeedType.HABIT_SKILL
    )
    
    response = await orchestrator.execute_agent_task(request, test_user.id)
    
    assert response.success
    assert response.agent_type == AgentType.COACH
    assert "phases" in response.result
    assert len(response.next_steps) > 0


@pytest.mark.asyncio
async def test_strategist_agent_fallback(db_session, test_user):
    """Test de l'agent Stratège en mode fallback"""
    orchestrator = MultiAgentOrchestratorService(db_session)
    
    request = AgentTaskRequest(
        agent_type=AgentType.STRATEGIST,
        user_input="Créer une application mobile",
        need_type=NeedType.COMPLEX_PROJECT
    )
    
    response = await orchestrator.execute_agent_task(request, test_user.id)
    
    assert response.success
    assert response.agent_type == AgentType.STRATEGIST
    assert "phases" in response.result
    assert "total_duration_weeks" in response.result


@pytest.mark.asyncio
async def test_planner_agent_fallback(db_session, test_user):
    """Test de l'agent Planificateur en mode fallback"""
    orchestrator = MultiAgentOrchestratorService(db_session)
    
    request = AgentTaskRequest(
        agent_type=AgentType.PLANNER,
        user_input="Planifier un voyage de 2 semaines",
        need_type=NeedType.PUNCTUAL_TASK
    )
    
    response = await orchestrator.execute_agent_task(request, test_user.id)
    
    assert response.success
    assert response.agent_type == AgentType.PLANNER
    assert "tasks" in response.result


@pytest.mark.asyncio
async def test_resource_agent_fallback(db_session, test_user):
    """Test de l'agent Ressources en mode fallback"""
    orchestrator = MultiAgentOrchestratorService(db_session)
    
    request = AgentTaskRequest(
        agent_type=AgentType.RESOURCE,
        user_input="Identifier les ressources pour un projet",
        need_type=NeedType.COMPLEX_PROJECT
    )
    
    response = await orchestrator.execute_agent_task(request, test_user.id)
    
    assert response.success
    assert response.agent_type == AgentType.RESOURCE
    assert "required_resources" in response.result


@pytest.mark.asyncio
async def test_research_agent_fallback(db_session, test_user):
    """Test de l'agent Recherche en mode fallback"""
    orchestrator = MultiAgentOrchestratorService(db_session)
    
    request = AgentTaskRequest(
        agent_type=AgentType.RESEARCH,
        user_input="Comparer les smartphones",
        need_type=NeedType.DECISION_RESEARCH
    )
    
    response = await orchestrator.execute_agent_task(request, test_user.id)
    
    assert response.success
    assert response.agent_type == AgentType.RESEARCH
    assert "options" in response.result
    assert "recommendation" in response.result


@pytest.mark.asyncio
async def test_social_agent_fallback(db_session, test_user):
    """Test de l'agent Social en mode fallback"""
    orchestrator = MultiAgentOrchestratorService(db_session)
    
    request = AgentTaskRequest(
        agent_type=AgentType.SOCIAL,
        user_input="Organiser une fête d'anniversaire",
        need_type=NeedType.SOCIAL_EVENT
    )
    
    response = await orchestrator.execute_agent_task(request, test_user.id)
    
    assert response.success
    assert response.agent_type == AgentType.SOCIAL
    assert "timeline" in response.result


@pytest.mark.asyncio
async def test_executive_agent_fallback(db_session, test_user):
    """Test de l'agent Exécutif en mode fallback"""
    orchestrator = MultiAgentOrchestratorService(db_session)
    
    request = AgentTaskRequest(
        agent_type=AgentType.EXECUTIVE,
        user_input="Acheter un cadeau",
        need_type=NeedType.PUNCTUAL_TASK
    )
    
    response = await orchestrator.execute_agent_task(request, test_user.id)
    
    assert response.success
    assert response.agent_type == AgentType.EXECUTIVE
    assert "steps" in response.result


# Tests pour OrchestrationService

@pytest.mark.asyncio
async def test_orchestrated_plan_punctual_task(db_session, test_user):
    """Test d'un plan orchestré pour une tâche ponctuelle"""
    orchestration = OrchestrationService(db_session)
    
    request = OrchestratedPlanRequest(
        user_input="Réserver un restaurant",
        create_goals=False
    )
    
    response = await orchestration.create_orchestrated_plan(request, test_user.id)
    
    assert response.classification.need_type == NeedType.PUNCTUAL_TASK
    assert len(response.agent_responses) > 0
    assert response.integrated_plan["need_type"] == NeedType.PUNCTUAL_TASK.value
    assert len(response.summary) > 0


@pytest.mark.asyncio
async def test_orchestrated_plan_creates_goal(db_session, test_user):
    """Test que l'orchestration crée un objectif pour une habitude"""
    orchestration = OrchestrationService(db_session)
    
    # Compter les objectifs avant
    goals_before = db_session.query(Goal).filter(Goal.user_id == test_user.id).count()
    
    request = OrchestratedPlanRequest(
        user_input="Apprendre l'espagnol en 6 mois",
        create_goals=True
    )
    
    response = await orchestration.create_orchestrated_plan(request, test_user.id)
    
    # Vérifier qu'un objectif a été créé
    goals_after = db_session.query(Goal).filter(Goal.user_id == test_user.id).count()
    
    assert response.classification.need_type == NeedType.HABIT_SKILL
    assert goals_after > goals_before or len(response.created_goals) > 0


@pytest.mark.asyncio
async def test_orchestrated_plan_complex_project(db_session, test_user):
    """Test d'un plan orchestré pour un projet complexe"""
    orchestration = OrchestrationService(db_session)
    
    request = OrchestratedPlanRequest(
        user_input="Créer une startup technologique",
        create_goals=True
    )
    
    response = await orchestration.create_orchestrated_plan(request, test_user.id)
    
    assert response.classification.need_type == NeedType.COMPLEX_PROJECT
    # Doit avoir plusieurs agents activés
    assert len(response.agent_responses) >= 2
    # Vérifier que les agents appropriés sont présents
    agent_types = [r.agent_type for r in response.agent_responses]
    assert AgentType.STRATEGIST in agent_types or AgentType.PLANNER in agent_types


@pytest.mark.asyncio
async def test_integration_of_agent_results(db_session, test_user):
    """Test de l'intégration des résultats d'agents multiples"""
    orchestration = OrchestrationService(db_session)
    
    request = OrchestratedPlanRequest(
        user_input="Organiser un mariage en 12 mois",
        create_goals=True
    )
    
    response = await orchestration.create_orchestrated_plan(request, test_user.id)
    
    # Vérifier l'intégration
    assert "agents_used" in response.integrated_plan
    assert "consolidated_next_steps" in response.integrated_plan
    assert len(response.integrated_plan["consolidated_next_steps"]) > 0
    
    # Vérifier le résumé
    assert "Social" in response.summary or "mariage" in response.summary.lower()


def test_get_agents_for_need_type(db_session):
    """Test de la correspondance type de besoin -> agents"""
    classifier = NeedClassifierService(db_session)
    
    # Tâche ponctuelle -> Exécutif
    agents = classifier._get_agents_for_need_type(NeedType.PUNCTUAL_TASK)
    assert AgentType.EXECUTIVE in agents
    
    # Habitude -> Coach + Planificateur
    agents = classifier._get_agents_for_need_type(NeedType.HABIT_SKILL)
    assert AgentType.COACH in agents
    assert AgentType.PLANNER in agents
    
    # Projet complexe -> Multi-agents
    agents = classifier._get_agents_for_need_type(NeedType.COMPLEX_PROJECT)
    assert len(agents) >= 3
    assert AgentType.STRATEGIST in agents
    
    # Recherche -> Agent Recherche
    agents = classifier._get_agents_for_need_type(NeedType.DECISION_RESEARCH)
    assert AgentType.RESEARCH in agents
    
    # Social -> Agent Social
    agents = classifier._get_agents_for_need_type(NeedType.SOCIAL_EVENT)
    assert AgentType.SOCIAL in agents


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
