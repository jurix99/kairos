"""
Service d'orchestration multi-agents (Niveau 2)
Coordonne les agents spécialisés pour résoudre les besoins complexes
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..models.database import Goal, Event
from ..models.schemas import (
    AgentType,
    NeedType,
    AgentTaskRequest,
    AgentTaskResponse,
    CoachPlan,
    ProjectPlan,
    ProjectPhase,
    ResourceAnalysis,
    ResourceRequirement,
    ResearchAnalysis,
    ComparisonCriteria,
    ComparisonOption,
    SocialEventPlan,
    PriorityLevel,
    GoalStatus,
    GoalCategory,
    GoalCreate
)
from .goal_service import GoalService


class MultiAgentOrchestratorService:
    """
    Service d'orchestration des agents spécialisés
    Niveau 2 : Coordination des modules spécialisés
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.goal_service = GoalService(db)
    
    def _normalize_next_steps(self, steps: any) -> List[str]:
        """
        Normalise les next_steps pour s'assurer qu'ils sont des strings
        """
        if not steps:
            return []
        
        if isinstance(steps, str):
            return [steps]
        
        if isinstance(steps, list):
            normalized = []
            for step in steps:
                if isinstance(step, str):
                    normalized.append(step)
                elif isinstance(step, dict):
                    # Si c'est un dict, essayer d'extraire un champ texte
                    normalized.append(step.get('title') or step.get('description') or step.get('step') or str(step))
                else:
                    normalized.append(str(step))
            return normalized
        
        return [str(steps)]
    
    async def execute_agent_task(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Exécute une tâche avec l'agent approprié
        """
        self.logger.info(f"Exécution de la tâche pour l'agent {request.agent_type}")
        
        if request.agent_type == AgentType.COACH:
            return await self._execute_coach_agent(request, user_id)
        elif request.agent_type == AgentType.STRATEGIST:
            return await self._execute_strategist_agent(request, user_id)
        elif request.agent_type == AgentType.PLANNER:
            return await self._execute_planner_agent(request, user_id)
        elif request.agent_type == AgentType.RESOURCE:
            return await self._execute_resource_agent(request, user_id)
        elif request.agent_type == AgentType.RESEARCH:
            return await self._execute_research_agent(request, user_id)
        elif request.agent_type == AgentType.SOCIAL:
            return await self._execute_social_agent(request, user_id)
        elif request.agent_type == AgentType.EXECUTIVE:
            return await self._execute_executive_agent(request, user_id)
        else:
            raise ValueError(f"Agent type not supported: {request.agent_type}")
    
    async def _execute_coach_agent(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Agent Coach : Pour habitudes et compétences
        Décompose en étapes progressives avec feedback
        """
        self.logger.info("Exécution de l'agent Coach")
        
        if not self.client:
            return self._fallback_coach_response(request)
        
        system_prompt = """Tu es un coach expert en développement personnel et formation de compétences.
Ta mission est de créer un plan progressif et réaliste pour aider l'utilisateur à atteindre son objectif.

Structure ton plan en:
1. Phases progressives (3-5 phases) avec durée et objectifs clairs
2. Fréquence recommandée par semaine
3. Jalons importants (milestones)
4. Métriques de succès pour suivre les progrès

Sois spécifique, motivant et réaliste. Considère la progression graduelle.
Retourne un JSON avec: phases, duration_weeks, frequency_per_week, milestones, success_metrics"""

        user_prompt = f"""Objectif: {request.user_input}

Contexte: {json.dumps(request.context) if request.context else 'Aucun contexte additionnel'}

Crée un plan progressif détaillé."""
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            # S'assurer que success_metrics est une liste de strings
            success_metrics = result.get('success_metrics', [])
            if success_metrics and isinstance(success_metrics[0], dict):
                success_metrics = [str(metric) for metric in success_metrics]
            
            # Créer un objectif dans la base de données
            goal_data = GoalCreate(
                title=request.user_input,
                description=f"Plan d'entraînement progressif sur {result.get('duration_weeks', 12)} semaines",
                target_date=datetime.now() + timedelta(weeks=result.get('duration_weeks', 12)),
                priority=PriorityLevel.MEDIUM,
                status=GoalStatus.ACTIVE,
                category=GoalCategory.PERSONAL,
                strategy=json.dumps(result, ensure_ascii=False),
                success_criteria="\n".join(success_metrics) if success_metrics else ""
            )
            
            created_goal = self.goal_service.create_goal(goal_data, user_id)
            
            return AgentTaskResponse(
                agent_type=AgentType.COACH,
                success=True,
                result=result,
                message=f"Plan progressif créé avec succès sur {result.get('duration_weeks', 12)} semaines",
                next_steps=[
                    "Commencer par la Phase 1",
                    "Suivre la progression hebdomadaire",
                    "Ajuster selon les résultats"
                ],
                created_goals=[created_goal.id]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'agent Coach: {e}")
            return AgentTaskResponse(
                agent_type=AgentType.COACH,
                success=False,
                result={},
                message=f"Erreur lors de la création du plan: {str(e)}",
                next_steps=[]
            )
    
    async def _execute_strategist_agent(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Agent Stratège : Définit les grandes phases d'un projet
        """
        self.logger.info("Exécution de l'agent Stratège")
        
        if not self.client:
            return self._fallback_strategist_response(request)
        
        system_prompt = """Tu es un stratège expert en gestion de projet.
Ta mission est de décomposer le projet en phases majeures avec:
- Numéro de phase
- Titre et description
- Durée estimée en semaines
- Dépendances entre phases
- Livrables attendus

Retourne un JSON avec: title, phases (liste), total_duration_weeks, critical_path"""

        user_prompt = f"""Projet: {request.user_input}

Contexte: {json.dumps(request.context) if request.context else 'Aucun'}

Définis les phases stratégiques du projet."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Créer un objectif pour le projet
            goal_data = GoalCreate(
                title=result.get('title', request.user_input),
                description=f"Projet en {len(result.get('phases', []))} phases",
                target_date=datetime.now() + timedelta(weeks=result.get('total_duration_weeks', 12)),
                priority=PriorityLevel.HIGH,
                status=GoalStatus.ACTIVE,
                category=GoalCategory.CAREER,
                strategy=json.dumps(result, ensure_ascii=False)
            )
            
            created_goal = self.goal_service.create_goal(goal_data, user_id)
            
            return AgentTaskResponse(
                agent_type=AgentType.STRATEGIST,
                success=True,
                result=result,
                message=f"Stratégie de projet définie en {len(result.get('phases', []))} phases",
                next_steps=[
                    "Détailler chaque phase avec l'agent Planificateur",
                    "Identifier les ressources nécessaires",
                    "Créer les tâches de la première phase"
                ],
                created_goals=[created_goal.id]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur agent Stratège: {e}")
            return AgentTaskResponse(
                agent_type=AgentType.STRATEGIST,
                success=False,
                result={},
                message=f"Erreur: {str(e)}",
                next_steps=[]
            )
    
    async def _execute_planner_agent(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Agent Planificateur : Estime durées et crée un planning détaillé
        """
        self.logger.info("Exécution de l'agent Planificateur")
        
        if not self.client:
            return self._fallback_planner_response(request)
        
        system_prompt = """Tu es un planificateur expert.
Crée un planning détaillé avec:
- Tâches spécifiques
- Durées estimées
- Dépendances entre tâches
- Dates recommandées

Retourne un JSON avec: tasks (liste de tâches), timeline, critical_tasks"""

        user_prompt = f"""Objectif: {request.user_input}

Contexte: {json.dumps(request.context) if request.context else 'Aucun'}

Crée un planning détaillé."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return AgentTaskResponse(
                agent_type=AgentType.PLANNER,
                success=True,
                result=result,
                message=f"Planning créé avec {len(result.get('tasks', []))} tâches",
                next_steps=[
                    "Créer les événements dans le calendrier",
                    "Configurer les rappels",
                    "Commencer par les tâches critiques"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur agent Planificateur: {e}")
            return AgentTaskResponse(
                agent_type=AgentType.PLANNER,
                success=False,
                result={},
                message=f"Erreur: {str(e)}",
                next_steps=[]
            )
    
    async def _execute_resource_agent(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Agent Ressources : Identifie les ressources nécessaires
        """
        self.logger.info("Exécution de l'agent Ressources")
        
        if not self.client:
            return self._fallback_resource_response(request)
        
        system_prompt = """Tu es un expert en gestion des ressources.
Identifie toutes les ressources nécessaires:
- Budget et coûts estimés
- Outils et logiciels
- Compétences requises
- Ressources humaines
- Alternatives possibles

Retourne un JSON avec: required_resources, total_estimated_budget, missing_skills, recommended_tools"""

        user_prompt = f"""Projet/Objectif: {request.user_input}

Contexte: {json.dumps(request.context) if request.context else 'Aucun'}

Liste les ressources nécessaires."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return AgentTaskResponse(
                agent_type=AgentType.RESOURCE,
                success=True,
                result=result,
                message=f"Analyse des ressources complétée",
                next_steps=[
                    "Valider le budget",
                    "Acquérir les outils nécessaires",
                    "Former les compétences manquantes"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur agent Ressources: {e}")
            return AgentTaskResponse(
                agent_type=AgentType.RESOURCE,
                success=False,
                result={},
                message=f"Erreur: {str(e)}",
                next_steps=[]
            )
    
    async def _execute_research_agent(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Agent Recherche : Compare options et synthétise informations
        """
        self.logger.info("Exécution de l'agent Recherche")
        
        if not self.client:
            return self._fallback_research_response(request)
        
        system_prompt = """Tu es un analyste expert en recherche et comparaison.
Analyse les options disponibles avec:
- Critères de comparaison pertinents
- Évaluation de chaque option
- Points forts et faibles
- Recommandation finale avec justification

Retourne un JSON avec: question, criteria, options, recommendation, reasoning"""

        user_prompt = f"""Question/Décision: {request.user_input}

Contexte: {json.dumps(request.context) if request.context else 'Aucun'}

Compare les options et recommande."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return AgentTaskResponse(
                agent_type=AgentType.RESEARCH,
                success=True,
                result=result,
                message="Analyse comparative complétée",
                next_steps=[
                    "Valider la recommandation",
                    "Approfondir si nécessaire",
                    "Prendre la décision finale"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur agent Recherche: {e}")
            return AgentTaskResponse(
                agent_type=AgentType.RESEARCH,
                success=False,
                result={},
                message=f"Erreur: {str(e)}",
                next_steps=[]
            )
    
    async def _execute_social_agent(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Agent Social : Gère les événements sociaux
        """
        self.logger.info("Exécution de l'agent Social")
        
        if not self.client:
            return self._fallback_social_response(request)
        
        system_prompt = """Tu es un expert en organisation d'événements.
Crée un plan complet pour l'événement avec:
- Type d'événement
- Timeline des tâches (ordre chronologique)
- Détails logistiques (lieu, restauration, etc.)
- Gestion des invités
- Budget estimé

Retourne un JSON avec: event_type, guest_count, budget, timeline, logistics, guest_management"""

        user_prompt = f"""Événement: {request.user_input}

Contexte: {json.dumps(request.context) if request.context else 'Aucun'}

Planifie l'événement."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            event_type = result.get('event_type', "l'événement")
            return AgentTaskResponse(
                agent_type=AgentType.SOCIAL,
                success=True,
                result=result,
                message=f"Plan d'événement créé pour {event_type}",
                next_steps=[
                    "Réserver le lieu",
                    "Envoyer les invitations",
                    "Confirmer les prestataires"
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Erreur agent Social: {e}")
            return AgentTaskResponse(
                agent_type=AgentType.SOCIAL,
                success=False,
                result={},
                message=f"Erreur: {str(e)}",
                next_steps=[]
            )
    
    async def _execute_executive_agent(
        self,
        request: AgentTaskRequest,
        user_id: int
    ) -> AgentTaskResponse:
        """
        Agent Exécutif : Génère des tâches actionables pour des besoins simples
        """
        self.logger.info("Exécution de l'agent Exécutif")
        
        if not self.client:
            return self._fallback_executive_response(request)
        
        system_prompt = """Tu es un assistant exécutif efficace.
Transforme la demande en étapes d'action concrètes et simples.

Retourne un JSON avec: task_title, steps (liste d'actions), estimated_time, priority"""

        user_prompt = f"""Tâche: {request.user_input}

Contexte: {json.dumps(request.context) if request.context else 'Aucun'}

Définis les étapes d'action."""

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            return AgentTaskResponse(
                agent_type=AgentType.EXECUTIVE,
                success=True,
                result=result,
                message=f"Tâche décomposée en {len(result.get('steps', []))} étapes",
                next_steps=self._normalize_next_steps(result.get('steps', []))
            )
            
        except Exception as e:
            self.logger.error(f"Erreur agent Exécutif: {e}")
            return AgentTaskResponse(
                agent_type=AgentType.EXECUTIVE,
                success=False,
                result={},
                message=f"Erreur: {str(e)}",
                next_steps=[]
            )
    
    # Méthodes de fallback si OpenAI n'est pas disponible
    
    def _fallback_coach_response(self, request: AgentTaskRequest) -> AgentTaskResponse:
        """Réponse de fallback pour l'agent Coach"""
        result = {
            "phases": [
                {"phase": 1, "title": "Démarrage", "duration_weeks": 2, "description": "Commencer progressivement"},
                {"phase": 2, "title": "Développement", "duration_weeks": 4, "description": "Augmenter l'intensité"},
                {"phase": 3, "title": "Consolidation", "duration_weeks": 6, "description": "Maintenir et perfectionner"}
            ],
            "duration_weeks": 12,
            "frequency_per_week": 3,
            "milestones": ["Fin de phase 1", "Mi-parcours", "Objectif atteint"],
            "success_metrics": ["Progression régulière", "Constance", "Résultats mesurables"]
        }
        
        return AgentTaskResponse(
            agent_type=AgentType.COACH,
            success=True,
            result=result,
            message="Plan progressif créé (mode basique - OpenAI non disponible)",
            next_steps=["Commencer la phase 1", "Suivre la progression"]
        )
    
    def _fallback_strategist_response(self, request: AgentTaskRequest) -> AgentTaskResponse:
        """Réponse de fallback pour l'agent Stratège"""
        result = {
            "title": request.user_input,
            "phases": [
                {"phase_number": 1, "title": "Planification", "estimated_duration_weeks": 2, "dependencies": []},
                {"phase_number": 2, "title": "Exécution", "estimated_duration_weeks": 8, "dependencies": [1]},
                {"phase_number": 3, "title": "Finalisation", "estimated_duration_weeks": 2, "dependencies": [2]}
            ],
            "total_duration_weeks": 12,
            "critical_path": [1, 2, 3]
        }
        
        return AgentTaskResponse(
            agent_type=AgentType.STRATEGIST,
            success=True,
            result=result,
            message="Stratégie de base créée (mode basique)",
            next_steps=["Détailler les phases"]
        )
    
    def _fallback_planner_response(self, request: AgentTaskRequest) -> AgentTaskResponse:
        """Réponse de fallback pour l'agent Planificateur"""
        result = {
            "tasks": [
                {"title": "Tâche 1", "duration_days": 7},
                {"title": "Tâche 2", "duration_days": 14},
                {"title": "Tâche 3", "duration_days": 7}
            ],
            "timeline": "4 semaines",
            "critical_tasks": ["Tâche 2"]
        }
        
        return AgentTaskResponse(
            agent_type=AgentType.PLANNER,
            success=True,
            result=result,
            message="Planning de base créé",
            next_steps=["Ajouter au calendrier"]
        )
    
    def _fallback_resource_response(self, request: AgentTaskRequest) -> AgentTaskResponse:
        """Réponse de fallback pour l'agent Ressources"""
        result = {
            "required_resources": [
                {"resource_type": "budget", "name": "Budget initial", "priority": "high"}
            ],
            "total_estimated_budget": "À déterminer",
            "missing_skills": [],
            "recommended_tools": ["Outils standard"]
        }
        
        return AgentTaskResponse(
            agent_type=AgentType.RESOURCE,
            success=True,
            result=result,
            message="Analyse de ressources de base",
            next_steps=["Valider les besoins"]
        )
    
    def _fallback_research_response(self, request: AgentTaskRequest) -> AgentTaskResponse:
        """Réponse de fallback pour l'agent Recherche"""
        result = {
            "question": request.user_input,
            "criteria": [{"name": "Prix", "weight": 0.3}, {"name": "Qualité", "weight": 0.7}],
            "options": [
                {"name": "Option A", "pros": ["Abordable"], "cons": ["Basique"]},
                {"name": "Option B", "pros": ["Complet"], "cons": ["Cher"]}
            ],
            "recommendation": "À analyser plus en détail",
            "reasoning": "Comparaison préliminaire nécessitant plus d'informations"
        }
        
        return AgentTaskResponse(
            agent_type=AgentType.RESEARCH,
            success=True,
            result=result,
            message="Analyse de base effectuée",
            next_steps=["Approfondir la recherche"]
        )
    
    def _fallback_social_response(self, request: AgentTaskRequest) -> AgentTaskResponse:
        """Réponse de fallback pour l'agent Social"""
        result = {
            "event_type": "Événement social",
            "timeline": [
                {"task": "Planifier", "weeks_before": 8},
                {"task": "Inviter", "weeks_before": 4},
                {"task": "Confirmer", "weeks_before": 1}
            ],
            "logistics": {"lieu": "À déterminer", "restauration": "À planifier"},
            "guest_management": {"invitations": "À envoyer"}
        }
        
        return AgentTaskResponse(
            agent_type=AgentType.SOCIAL,
            success=True,
            result=result,
            message="Plan d'événement de base créé",
            next_steps=["Réserver le lieu", "Envoyer les invitations"]
        )
    
    def _fallback_executive_response(self, request: AgentTaskRequest) -> AgentTaskResponse:
        """Réponse de fallback pour l'agent Exécutif"""
        result = {
            "task_title": request.user_input,
            "steps": [
                "Étape 1: Préparation",
                "Étape 2: Exécution",
                "Étape 3: Vérification"
            ],
            "estimated_time": "Variable",
            "priority": "medium"
        }
        
        return AgentTaskResponse(
            agent_type=AgentType.EXECUTIVE,
            success=True,
            result=result,
            message="Tâche décomposée en étapes de base",
            next_steps=result["steps"]
        )
