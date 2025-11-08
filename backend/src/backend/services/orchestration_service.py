"""
Service d'orchestration principal
Combine la classification des besoins et l'exécution des agents
"""

import logging
from typing import List
from sqlalchemy.orm import Session

from ..models.schemas import (
    NeedClassificationRequest,
    OrchestratedPlanRequest,
    OrchestratedPlanResponse,
    AgentTaskRequest,
    AgentTaskResponse
)
from .need_classifier_service import NeedClassifierService
from .multi_agent_orchestrator_service import MultiAgentOrchestratorService


class OrchestrationService:
    """
    Service principal d'orchestration
    Combine tous les niveaux du système multi-agents
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.classifier = NeedClassifierService(db)
        self.multi_agent = MultiAgentOrchestratorService(db)
    
    async def create_orchestrated_plan(
        self,
        request: OrchestratedPlanRequest,
        user_id: int
    ) -> OrchestratedPlanResponse:
        """
        Crée un plan orchestré complet:
        1. Classifie le besoin
        2. Active les agents appropriés
        3. Intègre les résultats
        4. Crée les objectifs/événements si demandé
        """
        self.logger.info(f"Création d'un plan orchestré pour: {request.user_input[:100]}")
        
        # Niveau 1: Classification du besoin
        classification_request = NeedClassificationRequest(
            user_input=request.user_input,
            context=None
        )
        
        classification = await self.classifier.classify_need(classification_request)
        self.logger.info(f"Besoin classifié comme: {classification.need_type} "
                        f"(confiance: {classification.confidence:.2f})")
        
        # Niveau 2: Exécution des agents suggérés
        agent_responses: List[AgentTaskResponse] = []
        
        for agent_type in classification.suggested_agents:
            self.logger.info(f"Exécution de l'agent: {agent_type}")
            
            agent_request = AgentTaskRequest(
                agent_type=agent_type,
                user_input=request.user_input,
                need_type=classification.need_type,
                context={
                    "complexity": classification.complexity.value,
                    "key_characteristics": classification.key_characteristics
                }
            )
            
            try:
                agent_response = await self.multi_agent.execute_agent_task(
                    agent_request,
                    user_id
                )
                agent_responses.append(agent_response)
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'exécution de l'agent {agent_type}: {e}")
                # Continue avec les autres agents
                continue
        
        # Intégrer les résultats
        integrated_plan = self._integrate_agent_results(
            classification,
            agent_responses,
            request
        )
        
        # Collecter les IDs des objectifs et événements créés
        created_goals = []
        created_events = []
        
        for response in agent_responses:
            if response.success:
                created_goals.extend(response.created_goals)
                created_events.extend(response.created_events)
        
        # Générer un résumé
        summary = self._generate_summary(classification, agent_responses)
        
        return OrchestratedPlanResponse(
            classification=classification,
            agent_responses=agent_responses,
            integrated_plan=integrated_plan,
            summary=summary,
            created_goals=created_goals,
            created_events=created_events
        )
    
    def _integrate_agent_results(
        self,
        classification,
        agent_responses: List[AgentTaskResponse],
        request: OrchestratedPlanRequest
    ) -> dict:
        """
        Intègre les résultats de tous les agents en un plan cohérent
        """
        integrated = {
            "need_type": classification.need_type.value,
            "complexity": classification.complexity.value,
            "confidence": classification.confidence,
            "reasoning": classification.reasoning,
            "key_characteristics": classification.key_characteristics,
            "agents_used": [],
            "results": {},
            "consolidated_next_steps": []
        }
        
        for response in agent_responses:
            if response.success:
                integrated["agents_used"].append(response.agent_type.value)
                integrated["results"][response.agent_type.value] = response.result
                integrated["consolidated_next_steps"].extend(response.next_steps)
        
        # Dédupliquer les prochaines étapes
        integrated["consolidated_next_steps"] = list(set(integrated["consolidated_next_steps"]))
        
        return integrated
    
    def _generate_summary(
        self,
        classification,
        agent_responses: List[AgentTaskResponse]
    ) -> str:
        """
        Génère un résumé textuel du plan orchestré
        """
        summary_parts = []
        
        # Classification
        summary_parts.append(
            f"Votre besoin a été identifié comme: {classification.need_type.value.replace('_', ' ').title()}"
        )
        summary_parts.append(
            f"Niveau de complexité: {classification.complexity.value}"
        )
        
        # Agents activés
        successful_agents = [r for r in agent_responses if r.success]
        if successful_agents:
            agents_list = ", ".join([r.agent_type.value.title() for r in successful_agents])
            summary_parts.append(
                f"Agents mobilisés: {agents_list}"
            )
        
        # Résultats clés
        for response in successful_agents:
            if response.message:
                summary_parts.append(f"• {response.agent_type.value.title()}: {response.message}")
        
        # Prochaines étapes
        all_next_steps = []
        for response in successful_agents:
            all_next_steps.extend(response.next_steps[:3])  # Max 3 par agent
        
        if all_next_steps:
            summary_parts.append("\nProchaines étapes recommandées:")
            for i, step in enumerate(all_next_steps[:5], 1):  # Max 5 au total
                summary_parts.append(f"{i}. {step}")
        
        return "\n".join(summary_parts)
