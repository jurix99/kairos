"""
Service de classification des besoins utilisateur (Niveau 1)
Identifie le type de besoin et active les bons agents
"""

import logging
import re
from typing import List, Optional
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..models.schemas import (
    NeedType,
    NeedComplexity,
    AgentType,
    NeedClassificationRequest,
    NeedClassificationResponse
)


class NeedClassifierService:
    """
    Service de classification des besoins utilisateur
    Niveau 1 : Comprendre et catégoriser le besoin
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        # Mots-clés pour la classification basique (fallback si pas d'OpenAI)
        self.keywords_map = {
            NeedType.PUNCTUAL_TASK: [
                'réserver', 'acheter', 'appeler', 'envoyer', 'poster', 
                'payer', 'chercher', 'trouver', 'contacter', 'commander'
            ],
            NeedType.HABIT_SKILL: [
                'apprendre', 'pratiquer', 'progresser', 'maîtriser', 'courir',
                'étudier', 'lire', 'méditer', 'exercice', 'habitude', 'régulier',
                'quotidien', 'hebdomadaire', 'entraîner', 'développer'
            ],
            NeedType.COMPLEX_PROJECT: [
                'créer', 'développer', 'lancer', 'construire', 'établir',
                'projet', 'entreprise', 'startup', 'application', 'site',
                'planifier', 'stratégie', 'étapes', 'phases'
            ],
            NeedType.DECISION_RESEARCH: [
                'choisir', 'comparer', 'décider', 'évaluer', 'sélectionner',
                'option', 'alternative', 'meilleur', 'recherche', 'analyse',
                'critère', 'comparaison'
            ],
            NeedType.SOCIAL_EVENT: [
                'organiser', 'inviter', 'fête', 'mariage', 'anniversaire',
                'réunion', 'événement', 'célébration', 'invités', 'réception',
                'soirée', 'party'
            ]
        }
    
    async def classify_need(
        self,
        request: NeedClassificationRequest
    ) -> NeedClassificationResponse:
        """
        Classifie le besoin utilisateur et suggère les agents appropriés
        """
        self.logger.info(f"Classification du besoin: {request.user_input[:100]}")
        
        # Si OpenAI est disponible, utiliser l'IA pour une classification avancée
        if self.client:
            try:
                return await self._classify_with_ai(request)
            except Exception as e:
                self.logger.warning(f"Erreur OpenAI, fallback vers classification basique: {e}")
        
        # Fallback: classification basée sur les mots-clés
        return self._classify_with_keywords(request)
    
    async def _classify_with_ai(
        self,
        request: NeedClassificationRequest
    ) -> NeedClassificationResponse:
        """
        Classification avancée avec OpenAI
        """
        system_prompt = """Tu es un expert en analyse de besoins et en gestion de projets.
Ta tâche est de classifier le besoin de l'utilisateur selon ces catégories:

1. PUNCTUAL_TASK: Tâche ponctuelle, action simple et court terme
   - Exemples: réserver un restaurant, acheter un cadeau, appeler quelqu'un
   
2. HABIT_SKILL: Habitude ou compétence à développer sur le long terme
   - Exemples: courir un marathon, apprendre une langue, méditer quotidiennement
   
3. COMPLEX_PROJECT: Projet complexe avec plusieurs étapes et dépendances
   - Exemples: créer une entreprise, développer une application, rénover une maison
   
4. DECISION_RESEARCH: Décision nécessitant recherche et comparaison
   - Exemples: choisir une assurance, acheter une voiture, sélectionner un fournisseur
   
5. SOCIAL_EVENT: Événement social nécessitant logistique et coordination
   - Exemples: organiser un mariage, planifier une fête, coordonner une réunion

Analyse le besoin et retourne une classification en JSON avec:
- need_type: le type de besoin
- complexity: SIMPLE, MODERATE, COMPLEX, ou VERY_COMPLEX
- confidence: score de 0 à 1
- reasoning: explication de ton analyse
- key_characteristics: liste des caractéristiques identifiées"""

        user_prompt = f"Besoin utilisateur: {request.user_input}"
        
        if request.context:
            user_prompt += f"\n\nContexte: {request.context}"
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = eval(response.choices[0].message.content)
        
        need_type = NeedType(result['need_type'].lower())
        complexity = NeedComplexity(result['complexity'].lower())
        suggested_agents = self._get_agents_for_need_type(need_type)
        
        return NeedClassificationResponse(
            need_type=need_type,
            complexity=complexity,
            suggested_agents=suggested_agents,
            confidence=result['confidence'],
            reasoning=result['reasoning'],
            key_characteristics=result.get('key_characteristics', [])
        )
    
    def _classify_with_keywords(
        self,
        request: NeedClassificationRequest
    ) -> NeedClassificationResponse:
        """
        Classification basique basée sur les mots-clés
        """
        user_input_lower = request.user_input.lower()
        
        # Compter les correspondances pour chaque type
        scores = {}
        for need_type, keywords in self.keywords_map.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            scores[need_type] = score
        
        # Trouver le type avec le meilleur score
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        # Si aucune correspondance, par défaut tâche ponctuelle
        if best_score == 0:
            best_type = NeedType.PUNCTUAL_TASK
            confidence = 0.3
        else:
            # Calculer la confiance basée sur le score
            total_keywords = sum(scores.values())
            confidence = min(0.9, 0.5 + (best_score / max(1, total_keywords)) * 0.4)
        
        # Déterminer la complexité basée sur la longueur et les mots-clés
        complexity = self._estimate_complexity(user_input_lower)
        
        # Identifier les caractéristiques
        characteristics = []
        if any(word in user_input_lower for word in ['long terme', 'plusieurs', 'multiple', 'étapes']):
            characteristics.append('Multi-étapes')
        if any(word in user_input_lower for word in ['urgent', 'rapidement', 'vite']):
            characteristics.append('Court terme')
        if any(word in user_input_lower for word in ['apprendre', 'progresser', 'améliorer']):
            characteristics.append('Développement progressif')
        if any(word in user_input_lower for word in ['budget', 'coût', 'prix']):
            characteristics.append('Contrainte budgétaire')
        
        suggested_agents = self._get_agents_for_need_type(best_type)
        
        reasoning = f"Classification basée sur l'analyse des mots-clés. Type identifié: {best_type.value}"
        
        return NeedClassificationResponse(
            need_type=best_type,
            complexity=complexity,
            suggested_agents=suggested_agents,
            confidence=confidence,
            reasoning=reasoning,
            key_characteristics=characteristics
        )
    
    def _estimate_complexity(self, text: str) -> NeedComplexity:
        """
        Estime la complexité basée sur le texte
        """
        # Indicateurs de complexité
        complex_indicators = ['projet', 'plusieurs', 'étapes', 'phases', 'long terme', 'mois', 'année']
        simple_indicators = ['simple', 'rapide', 'vite', 'aujourd\'hui', 'demain']
        
        complex_count = sum(1 for word in complex_indicators if word in text)
        simple_count = sum(1 for word in simple_indicators if word in text)
        
        word_count = len(text.split())
        
        if complex_count > 2 or word_count > 100:
            return NeedComplexity.VERY_COMPLEX
        elif complex_count > 0 or word_count > 50:
            return NeedComplexity.COMPLEX
        elif simple_count > 0 or word_count < 20:
            return NeedComplexity.SIMPLE
        else:
            return NeedComplexity.MODERATE
    
    def _get_agents_for_need_type(self, need_type: NeedType) -> List[AgentType]:
        """
        Retourne les agents suggérés pour un type de besoin
        """
        agent_mapping = {
            NeedType.PUNCTUAL_TASK: [AgentType.EXECUTIVE],
            NeedType.HABIT_SKILL: [AgentType.COACH, AgentType.PLANNER],
            NeedType.COMPLEX_PROJECT: [
                AgentType.STRATEGIST,
                AgentType.PLANNER,
                AgentType.RESOURCE,
                AgentType.EXECUTIVE
            ],
            NeedType.DECISION_RESEARCH: [AgentType.RESEARCH],
            NeedType.SOCIAL_EVENT: [AgentType.SOCIAL, AgentType.PLANNER]
        }
        
        return agent_mapping.get(need_type, [AgentType.EXECUTIVE])
