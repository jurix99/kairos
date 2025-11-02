"""
Service pour l'assistant IA utilisant OpenAI
"""

import json
import re
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..config.settings import settings
from ..models.database import User, Category
from ..models.schemas import EventCreate, PriorityLevel, EventStatus
from .event_service import EventService
from .category_service import CategoryService


class ExtractedEvent(BaseModel):
    """Modèle pour un événement extrait par l'IA"""
    title: str
    description: Optional[str] = None
    start_time: str  # Format ISO
    end_time: str  # Format ISO  
    location: Optional[str] = None
    priority: str = "medium"
    category_name: str = "Général"


class AssistantResponse(BaseModel):
    """Modèle pour la réponse de l'assistant"""
    message: str
    events: List[ExtractedEvent] = []
    action: str = "chat"  # "chat" ou "create_events"


class AssistantService:
    """Service pour l'assistant IA"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisation du service Assistant")
        
        try:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.logger.info(f"Client OpenAI initialisé avec le modèle: {settings.OPENAI_MODEL}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du client OpenAI: {e}")
            raise
            
        self.event_service = EventService(db)
        self.category_service = CategoryService(db)
    
    async def chat(self, message: str, user_id: int, conversation_history: List[Dict] = None) -> AssistantResponse:
        """
        Traite un message de chat avec l'assistant IA
        """
        self.logger.info(f"Début du traitement du message pour l'utilisateur {user_id}")
        self.logger.debug(f"Message reçu: {message[:100]}...")
        
        if conversation_history is None:
            conversation_history = []
            
        try:
            # Récupérer le contexte utilisateur
            self.logger.debug("Récupération du contexte utilisateur")
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                self.logger.warning(f"Utilisateur {user_id} non trouvé")
                return AssistantResponse(
                    message="Utilisateur non trouvé.",
                    action="chat"
                )
            
            self.logger.debug(f"Utilisateur trouvé: {user.name}")
            categories = self.category_service.get_all_categories(user_id)
            self.logger.debug(f"Nombre de catégories: {len(categories)}")
            
            # Récupérer les événements récents pour le contexte
            self.logger.debug("Récupération des événements récents")
            recent_events = self.event_service.get_all_events(
                user_id=user_id,
                start_date=datetime.now() - timedelta(days=7),
                end_date=datetime.now() + timedelta(days=30)
            )
            self.logger.debug(f"Nombre d'événements récents: {len(recent_events)}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du contexte: {e}")
            return AssistantResponse(
                message="Erreur lors de la récupération du contexte utilisateur.",
                action="chat"
            )
        
        # Construire le prompt système
        system_prompt = self._build_system_prompt(user, categories, recent_events)
        
        # Construire l'historique de conversation
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        try:
            # Vérifier si la clé API OpenAI est configurée
            self.logger.debug("Vérification de la configuration OpenAI")
            if not settings.OPENAI_API_KEY:
                self.logger.error("Clé API OpenAI non configurée")
                return AssistantResponse(
                    message="L'assistant IA n'est pas configuré. Veuillez configurer la clé API OpenAI.",
                    action="chat"
                )
            
            self.logger.debug(f"Clé API OpenAI configurée (longueur: {len(settings.OPENAI_API_KEY)})")
            
            # Appel à OpenAI avec la nouvelle API tools
            self.logger.info(f"Appel à OpenAI avec le modèle {settings.OPENAI_MODEL}")
            self.logger.debug(f"Nombre de messages dans l'historique: {len(messages)}")
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "extract_events",
                            "description": "Extraire des événements du message de l'utilisateur",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "events": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "title": {"type": "string"},
                                                "description": {"type": "string"},
                                                "start_time": {"type": "string", "format": "date-time"},
                                                "end_time": {"type": "string", "format": "date-time"},
                                                "location": {"type": "string"},
                                                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                                                "category_name": {"type": "string"}
                                            },
                                            "required": ["title", "start_time", "end_time", "category_name"]
                                        }
                                    }
                                },
                                "required": ["events"]
                            }
                        }
                    }
                ],
                tool_choice="auto"
            )
            
            self.logger.info("Réponse OpenAI reçue avec succès")
            
            message_content = response.choices[0].message
            self.logger.debug(f"Message reçu d'OpenAI: {message_content.content[:100] if message_content.content else 'Pas de contenu'}...")
            
            # Vérifier si des outils ont été appelés
            if message_content.tool_calls:
                self.logger.info(f"Outils appelés: {len(message_content.tool_calls)}")
                for tool_call in message_content.tool_calls:
                    self.logger.debug(f"Outil appelé: {tool_call.function.name}")
                    if tool_call.function.name == "extract_events":
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                            events_data = function_args.get("events", [])
                            self.logger.info(f"Événements extraits: {len(events_data)}")
                            
                            events = [ExtractedEvent(**event) for event in events_data]
                            
                            return AssistantResponse(
                                message=f"J'ai trouvé {len(events)} événement(s) dans votre message. Voulez-vous que je les ajoute à votre calendrier ?",
                                events=events,
                                action="create_events"
                            )
                        except Exception as e:
                            self.logger.error(f"Erreur lors du parsing des événements: {e}")
                            self.logger.error(f"Arguments de la fonction: {tool_call.function.arguments}")
            
            # Réponse normale de chat
            self.logger.info("Réponse de chat normale")
            return AssistantResponse(
                message=message_content.content or "Je n'ai pas pu traiter votre demande.",
                action="chat"
            )
            
        except Exception as e:
            self.logger.error(f"Erreur dans le service assistant: {e}")
            self.logger.error(f"Type d'erreur: {type(e).__name__}")
            self.logger.exception("Stack trace complète:")
            
            return AssistantResponse(
                message=f"Désolé, j'ai rencontré une erreur lors du traitement de votre message: {str(e)}",
                action="chat"
            )
    
    async def create_events_from_extracted(self, events: List[ExtractedEvent], user_id: int) -> List[int]:
        """
        Crée des événements à partir des données extraites par l'IA
        """
        self.logger.info(f"Création de {len(events)} événements pour l'utilisateur {user_id}")
        created_event_ids = []
        
        for i, event_data in enumerate(events):
            self.logger.debug(f"Traitement de l'événement {i+1}/{len(events)}: {event_data.title}")
            try:
                # Trouver ou créer la catégorie
                category = self._find_or_create_category(event_data.category_name, user_id)
                self.logger.debug(f"Catégorie assignée: {category.name} (ID: {category.id})")
                
                # Mapper la priorité
                priority = self._map_priority(event_data.priority)
                
                # Créer l'événement
                event_create = EventCreate(
                    title=event_data.title,
                    description=event_data.description,
                    start_time=datetime.fromisoformat(event_data.start_time.replace('Z', '+00:00')),
                    end_time=datetime.fromisoformat(event_data.end_time.replace('Z', '+00:00')),
                    location=event_data.location,
                    priority=priority,
                    status=EventStatus.PENDING,
                    category_id=category.id,
                    is_flexible=True
                )
                
                created_event = self.event_service.create_event(event_create, user_id)
                created_event_ids.append(created_event.id)
                self.logger.info(f"Événement créé avec succès: {event_data.title} (ID: {created_event.id})")
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la création de l'événement {event_data.title}: {e}")
                self.logger.exception("Stack trace:")
                continue
                
        return created_event_ids
    
    def _build_system_prompt(self, user: User, categories: List, recent_events: List) -> str:
        """Construit le prompt système avec le contexte utilisateur"""
        
        categories_str = ", ".join([cat.name for cat in categories])
        events_context = ""
        
        if recent_events:
            events_context = "Événements récents de l'utilisateur:\n"
            for event in recent_events[:5]:  # Limiter à 5 événements
                events_context += f"- {event.title} ({event.start_time.strftime('%d/%m/%Y %H:%M')})\n"
        
        return f"""Tu es un assistant IA pour l'application de calendrier Kairos. 
        
Utilisateur: {user.name if user else "Utilisateur"}
Catégories disponibles: {categories_str}

{events_context}

Tu peux aider l'utilisateur à:
1. Gérer son calendrier et ses événements  
2. Analyser sa productivité
3. Extraire des événements depuis du texte naturel
4. Donner des conseils sur l'organisation du temps

IMPORTANT pour l'extraction d'événements:
- Utilise PRIORITAIREMENT les catégories existantes de l'utilisateur: {categories_str}
- Si aucune catégorie existante ne correspond, utilise une catégorie appropriée générique
- Pour les événements professionnels, privilégie "Travail" si disponible
- Pour les événements personnels, privilégie "Personnel" si disponible
- Pour les urgences, privilégie "Urgent" si disponible
- Pour les loisirs, privilégie "Loisirs" si disponible
- Pour la santé, privilégie "Santé" si disponible

Quand l'utilisateur mentionne des rendez-vous, réunions, ou événements avec des dates/heures, utilise la fonction extract_events pour les extraire automatiquement.

Réponds toujours en français de manière amicale et professionnelle."""

    def _find_or_create_category(self, category_name: str, user_id: int) -> Category:
        """Trouve une catégorie existante ou en crée une nouvelle"""
        
        # Nettoyer le nom de catégorie
        category_name = category_name.strip()
        
        # Mapping intelligent pour associer les noms de l'IA aux catégories existantes
        category_mappings = {
            # Variations de "Travail"
            "work": "Travail",
            "professionnel": "Travail", 
            "bureau": "Travail",
            "job": "Travail",
            "boulot": "Travail",
            
            # Variations de "Personnel" 
            "personal": "Personnel",
            "perso": "Personnel",
            "privé": "Personnel",
            
            # Variations de "Santé"
            "health": "Santé",
            "medical": "Santé",
            "médical": "Santé",
            "docteur": "Santé",
            "medecin": "Santé",
            
            # Variations de "Loisirs"
            "loisir": "Loisirs",
            "hobby": "Loisirs",
            "détente": "Loisirs",
            "divertissement": "Loisirs",
            
            # Variations de "Urgent"
            "urgence": "Urgent",
            "priority": "Urgent",
            "priorité": "Urgent",
            "important": "Urgent"
        }
        
        # Vérifier le mapping intelligent
        mapped_name = category_mappings.get(category_name.lower())
        if mapped_name:
            self.logger.debug(f"Mapping appliqué: {category_name} -> {mapped_name}")
            category_name = mapped_name
        
        # 1. Chercher une correspondance exacte dans les catégories utilisateur
        category = self.db.query(Category).filter(
            Category.name.ilike(category_name),
            Category.user_id == user_id
        ).first()
        
        if category:
            self.logger.debug(f"Catégorie utilisateur trouvée: {category.name}")
            return category
        
        # 2. Chercher une correspondance exacte dans les catégories globales
        global_category = self.db.query(Category).filter(
            Category.name.ilike(category_name),
            Category.user_id.is_(None)
        ).first()
        
        if global_category:
            self.logger.debug(f"Catégorie globale trouvée: {global_category.name}")
            return global_category
            
        # 3. Chercher une correspondance partielle dans les catégories utilisateur
        partial_category = self.db.query(Category).filter(
            Category.name.ilike(f"%{category_name}%"),
            Category.user_id == user_id
        ).first()
        
        if partial_category:
            self.logger.debug(f"Catégorie utilisateur partielle trouvée: {partial_category.name}")
            return partial_category
            
        # 4. Chercher une correspondance partielle dans les catégories globales
        partial_global_category = self.db.query(Category).filter(
            Category.name.ilike(f"%{category_name}%"),
            Category.user_id.is_(None)
        ).first()
        
        if partial_global_category:
            self.logger.debug(f"Catégorie globale partielle trouvée: {partial_global_category.name}")
            return partial_global_category
            
        # 5. Aucune catégorie trouvée, en créer une nouvelle
        self.logger.info(f"Création d'une nouvelle catégorie: {category_name}")
        color_code = self._get_smart_color_for_category(category_name)
        new_category = Category(
            name=category_name,
            color_code=color_code,
            user_id=user_id
        )
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        
        return new_category
    
    def _map_priority(self, priority_str: str) -> PriorityLevel:
        """Mappe une chaîne de priorité vers l'enum PriorityLevel"""
        priority_map = {
            "low": PriorityLevel.LOW,
            "medium": PriorityLevel.MEDIUM, 
            "high": PriorityLevel.HIGH
        }
        return priority_map.get(priority_str.lower(), PriorityLevel.MEDIUM)
    
    def _get_smart_color_for_category(self, category_name: str) -> str:
        """Choisit une couleur intelligente basée sur le nom de la catégorie"""
        category_lower = category_name.lower()
        
        # Couleurs selon le type de catégorie
        color_mapping = {
            # Travail et professionnel
            "travail": "#3B82F6",  # Bleu
            "work": "#3B82F6",
            "réunion": "#6366F1",  # Indigo
            "meeting": "#6366F1",
            "projet": "#8B5CF6",   # Violet
            
            # Personnel et loisirs
            "personnel": "#10B981", # Vert
            "personal": "#10B981",
            "loisir": "#F59E0B",   # Orange
            "hobby": "#F59E0B",
            "sport": "#EF4444",    # Rouge
            "fitness": "#EF4444",
            
            # Santé et bien-être
            "santé": "#EC4899",    # Rose
            "health": "#EC4899",
            "médecin": "#EC4899",
            "doctor": "#EC4899",
            
            # Famille et social
            "famille": "#84CC16",  # Vert lime
            "family": "#84CC16",
            "ami": "#06B6D4",      # Cyan
            "friend": "#06B6D4",
            
            # Éducation et apprentissage
            "cours": "#8B5CF6",    # Violet
            "education": "#8B5CF6",
            "formation": "#8B5CF6",
            
            # Général et défaut
            "général": "#6B7280",  # Gris
            "general": "#6B7280",
        }
        
        # Chercher une correspondance dans le nom
        for keyword, color in color_mapping.items():
            if keyword in category_lower:
                return color
        
        # Couleur par défaut (bleu)
        return "#3B82F6"
