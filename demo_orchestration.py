#!/usr/bin/env python3
"""
Script de démonstration du système d'orchestration multi-agents
"""

import asyncio
import sys
import os

# Ajouter le chemin vers le backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.database import Base, User, Category
from backend.services.orchestration_service import OrchestrationService
from backend.models.schemas import OrchestratedPlanRequest


def setup_demo_database():
    """Configure une base de données de démonstration"""
    engine = create_engine("sqlite:///./demo_orchestration.db")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Vérifier si un utilisateur existe déjà
    user = db.query(User).first()
    if not user:
        user = User(
            external_id="demo_user",
            name="Demo User",
            email="demo@kairos.com",
            provider="demo"
        )
        db.add(user)
        
        # Ajouter des catégories par défaut
        categories = [
            Category(name="Personnel", color_code="#10B981", user_id=None),
            Category(name="Travail", color_code="#3B82F6", user_id=None),
            Category(name="Sport", color_code="#F59E0B", user_id=None),
        ]
        db.add_all(categories)
        
        db.commit()
    
    return db, user


async def demo_orchestration(user_input: str, db, user):
    """Démontre l'orchestration pour une demande utilisateur"""
    orchestration = OrchestrationService(db)
    
    print(f"\n{'='*80}")
    print(f"DEMANDE UTILISATEUR : {user_input}")
    print(f"{'='*80}\n")
    
    request = OrchestratedPlanRequest(
        user_input=user_input,
        create_goals=True
    )
    
    response = await orchestration.create_orchestrated_plan(request, user.id)
    
    # Afficher la classification
    print("📊 CLASSIFICATION")
    print(f"   Type de besoin : {response.classification.need_type.value}")
    print(f"   Complexité     : {response.classification.complexity.value}")
    print(f"   Confiance      : {response.classification.confidence:.2%}")
    print(f"   Raisonnement   : {response.classification.reasoning}")
    
    if response.classification.key_characteristics:
        print(f"   Caractéristiques:")
        for char in response.classification.key_characteristics:
            print(f"      - {char}")
    
    # Afficher les agents activés
    print(f"\n🤖 AGENTS ACTIVÉS ({len(response.agent_responses)})")
    for agent_response in response.agent_responses:
        status = "✓" if agent_response.success else "✗"
        print(f"   {status} {agent_response.agent_type.value.upper()}")
        print(f"      {agent_response.message}")
    
    # Afficher le résumé
    print(f"\n📝 RÉSUMÉ")
    print(f"   {response.summary}")
    
    # Afficher les ressources créées
    if response.created_goals:
        print(f"\n🎯 OBJECTIFS CRÉÉS : {len(response.created_goals)}")
        for goal_id in response.created_goals:
            print(f"   - Objectif #{goal_id}")
    
    if response.created_events:
        print(f"\n📅 ÉVÉNEMENTS CRÉÉS : {len(response.created_events)}")
    
    # Afficher les prochaines étapes
    if response.integrated_plan.get('consolidated_next_steps'):
        print(f"\n📋 PROCHAINES ÉTAPES")
        for i, step in enumerate(response.integrated_plan['consolidated_next_steps'][:5], 1):
            print(f"   {i}. {step}")
    
    print(f"\n{'='*80}\n")


async def main():
    """Fonction principale de démonstration"""
    print("\n🚀 DÉMONSTRATION DU SYSTÈME D'ORCHESTRATION MULTI-AGENTS")
    print("=" * 80)
    
    db, user = setup_demo_database()
    
    # Exemples de démonstration
    examples = [
        "Je veux apprendre le piano en 6 mois",
        "Réserver un restaurant italien pour ce soir",
        "Créer une startup dans l'intelligence artificielle",
        "Choisir la meilleure assurance habitation",
        "Organiser un mariage pour 100 invités en juin prochain"
    ]
    
    print("\nExemples disponibles:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print("\n0. Entrer une demande personnalisée")
    print("Q. Quitter")
    
    while True:
        choice = input("\nChoisissez une option (1-5, 0, Q) : ").strip()
        
        if choice.upper() == 'Q':
            print("\nAu revoir!")
            break
        
        try:
            if choice == '0':
                user_input = input("\nEntrez votre demande : ").strip()
                if not user_input:
                    print("Demande vide, veuillez réessayer.")
                    continue
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(examples):
                    user_input = examples[idx]
                else:
                    print("Option invalide, veuillez réessayer.")
                    continue
            
            await demo_orchestration(user_input, db, user)
            
            # Demander si continuer
            cont = input("\nTester un autre exemple ? (O/n) : ").strip().lower()
            if cont == 'n':
                print("\nAu revoir!")
                break
                
        except ValueError:
            print("Entrée invalide, veuillez réessayer.")
        except KeyboardInterrupt:
            print("\n\nInterruption utilisateur. Au revoir!")
            break
        except Exception as e:
            print(f"\nErreur: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
