#!/usr/bin/env python3
"""
Script de démonstration du moteur de règles de suggestions

Ce script crée des scénarios de test pour démontrer le fonctionnement
du moteur de règles et génère des suggestions.

Usage:
    python demo_suggestions.py
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajouter le chemin source au PYTHONPATH
sys.path.insert(0, 'src')

from backend.models.database import Base, User, Category, Event
from backend.models.schemas import EventStatus, PriorityLevel
from backend.services.rules_engine_service import RulesEngineService


def setup_database():
    """Configure la base de données en mémoire pour la démo"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def create_test_data(db):
    """Crée des données de test"""
    print("📊 Création des données de test...")
    
    # Créer un utilisateur
    user = User(
        external_id="demo_user_123",
        name="Demo User",
        email="demo@kairos.app",
        provider="google"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer des catégories
    categories = [
        Category(name="Travail", color_code="#8B5CF6", description="Tâches professionnelles"),
        Category(name="Personnel", color_code="#06B6D4", description="Activités personnelles"),
        Category(name="Santé", color_code="#F59E0B", description="Sport et bien-être"),
    ]
    
    for cat in categories:
        db.add(cat)
    db.commit()
    
    print(f"✅ Utilisateur créé: {user.name} ({user.email})")
    print(f"✅ {len(categories)} catégories créées")
    
    return user, categories


def demo_break_rule(db, user, categories):
    """Démo de la règle de pause"""
    print("\n" + "="*60)
    print("🔍 DÉMO 1: Règle de Pause")
    print("="*60)
    print("📝 Scénario: 4 heures de travail continu")
    
    work_category = categories[0]  # Travail
    now = datetime.now()
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Créer des événements de travail continu
    events = [
        Event(
            title="Réunion d'équipe",
            start_time=start_time,
            end_time=start_time + timedelta(hours=2),
            category_id=work_category.id,
            user_id=user.id,
            priority=PriorityLevel.HIGH,
            status=EventStatus.PENDING,
            is_flexible=False
        ),
        Event(
            title="Développement",
            start_time=start_time + timedelta(hours=2),
            end_time=start_time + timedelta(hours=4),
            category_id=work_category.id,
            user_id=user.id,
            priority=PriorityLevel.MEDIUM,
            status=EventStatus.IN_PROGRESS,
            is_flexible=True
        )
    ]
    
    for event in events:
        db.add(event)
        print(f"  📅 {event.title}: {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}")
    db.commit()
    
    # Générer les suggestions
    print("\n🤖 Génération des suggestions...")
    rules_service = RulesEngineService(db)
    suggestions = rules_service.generate_suggestions_for_user(user.id, start_time)
    
    # Afficher les suggestions de pause
    break_suggestions = [s for s in suggestions if s.type == "take_break"]
    if break_suggestions:
        print(f"\n✨ {len(break_suggestions)} suggestion(s) générée(s):")
        for suggestion in break_suggestions:
            print(f"\n  {suggestion.title}")
            print(f"  📋 {suggestion.description}")
            print(f"  🎯 Priorité: {suggestion.priority}")
            print(f"  ⏰ Expire: {suggestion.expires_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("❌ Aucune suggestion générée (inattendu)")


def demo_balance_rule(db, user, categories):
    """Démo de la règle d'équilibrage"""
    print("\n" + "="*60)
    print("🔍 DÉMO 2: Règle d'Équilibrage")
    print("="*60)
    print("📝 Scénario: 80% du temps en travail")
    
    work_category = categories[0]  # Travail
    personal_category = categories[1]  # Personnel
    now = datetime.now()
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Nettoyer les événements précédents
    db.query(Event).filter(Event.user_id == user.id).delete()
    db.commit()
    
    # 8 heures de travail
    events = [
        Event(
            title="Sprint de développement",
            start_time=start_time,
            end_time=start_time + timedelta(hours=8),
            category_id=work_category.id,
            user_id=user.id,
            priority=PriorityLevel.HIGH,
            status=EventStatus.IN_PROGRESS,
            is_flexible=False
        ),
        Event(
            title="Pause déjeuner",
            start_time=start_time + timedelta(hours=8),
            end_time=start_time + timedelta(hours=9),
            category_id=personal_category.id,
            user_id=user.id,
            priority=PriorityLevel.MEDIUM,
            status=EventStatus.PENDING,
            is_flexible=True
        )
    ]
    
    for event in events:
        db.add(event)
        category = db.query(Category).filter(Category.id == event.category_id).first()
        print(f"  📅 {event.title} ({category.name}): {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}")
    db.commit()
    
    # Générer les suggestions
    print("\n🤖 Génération des suggestions...")
    rules_service = RulesEngineService(db)
    suggestions = rules_service.generate_suggestions_for_user(user.id, start_time)
    
    # Afficher les suggestions d'équilibrage
    balance_suggestions = [s for s in suggestions if s.type == "balance_day"]
    if balance_suggestions:
        print(f"\n✨ {len(balance_suggestions)} suggestion(s) générée(s):")
        for suggestion in balance_suggestions:
            print(f"\n  {suggestion.title}")
            print(f"  📋 {suggestion.description}")
            print(f"  🎯 Priorité: {suggestion.priority}")
            print(f"  ⏰ Expire: {suggestion.expires_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("❌ Aucune suggestion générée (inattendu)")


def demo_move_event_rule(db, user, categories):
    """Démo de la règle de déplacement d'événement"""
    print("\n" + "="*60)
    print("🔍 DÉMO 3: Règle de Déplacement d'Événement")
    print("="*60)
    print("📝 Scénario: Événement reporté plusieurs fois")
    
    work_category = categories[0]  # Travail
    now = datetime.now()
    created_at = now - timedelta(days=5)  # Créé il y a 5 jours
    
    # Nettoyer les événements précédents
    db.query(Event).filter(Event.user_id == user.id).delete()
    db.commit()
    
    # Événement reporté
    event = Event(
        title="Révision du budget annuel",
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, hours=2),
        category_id=work_category.id,
        user_id=user.id,
        priority=PriorityLevel.MEDIUM,
        status=EventStatus.PENDING,
        is_flexible=True,
        created_at=created_at,
        updated_at=now  # Mis à jour récemment
    )
    db.add(event)
    db.commit()
    
    print(f"  📅 {event.title}")
    print(f"  📆 Créé: {event.created_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"  🔄 Dernière modification: {event.updated_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"  ⏰ Prévu: {event.start_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Générer les suggestions
    print("\n🤖 Génération des suggestions...")
    rules_service = RulesEngineService(db)
    suggestions = rules_service.generate_suggestions_for_user(user.id)
    
    # Afficher les suggestions de déplacement
    move_suggestions = [s for s in suggestions if s.type == "move_event"]
    if move_suggestions:
        print(f"\n✨ {len(move_suggestions)} suggestion(s) générée(s):")
        for suggestion in move_suggestions:
            print(f"\n  {suggestion.title}")
            print(f"  📋 {suggestion.description}")
            print(f"  🎯 Priorité: {suggestion.priority}")
            print(f"  🔗 Événement lié: ID {suggestion.related_event_id}")
            print(f"  ⏰ Expire: {suggestion.expires_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("❌ Aucune suggestion générée (inattendu)")


def demo_suggestion_lifecycle(db, user, categories):
    """Démo du cycle de vie d'une suggestion"""
    print("\n" + "="*60)
    print("🔍 DÉMO 4: Cycle de Vie d'une Suggestion")
    print("="*60)
    
    work_category = categories[0]
    now = datetime.now()
    start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Nettoyer
    db.query(Event).filter(Event.user_id == user.id).delete()
    db.query(Event).filter(Event.user_id == user.id).delete()
    db.commit()
    
    # Créer un événement pour déclencher une suggestion
    event = Event(
        title="Travail intensif",
        start_time=start_time,
        end_time=start_time + timedelta(hours=4),
        category_id=work_category.id,
        user_id=user.id,
        priority=PriorityLevel.HIGH,
        status=EventStatus.IN_PROGRESS,
        is_flexible=False
    )
    db.add(event)
    db.commit()
    
    # 1. Générer une suggestion
    print("\n1️⃣ Génération de la suggestion...")
    rules_service = RulesEngineService(db)
    suggestions = rules_service.generate_suggestions_for_user(user.id, start_time)
    
    if suggestions:
        suggestion = suggestions[0]
        print(f"   ✅ Suggestion créée: {suggestion.title}")
        print(f"   📊 Statut initial: {suggestion.status}")
        
        # 2. Récupérer les suggestions actives
        print("\n2️⃣ Récupération des suggestions actives...")
        active = rules_service.get_active_suggestions(user.id)
        print(f"   ✅ {len(active)} suggestion(s) active(s)")
        
        # 3. Accepter la suggestion
        print("\n3️⃣ Acceptation de la suggestion...")
        updated = rules_service.update_suggestion_status(suggestion.id, user.id, "accepted")
        print(f"   ✅ Statut mis à jour: {updated.status}")
        
        # 4. Vérifier que la suggestion n'est plus dans les actives
        print("\n4️⃣ Vérification des suggestions actives...")
        active_after = rules_service.get_active_suggestions(user.id)
        print(f"   ✅ {len(active_after)} suggestion(s) active(s)")
        
        # 5. Essayer de créer une suggestion en double
        print("\n5️⃣ Test de non-duplication...")
        duplicate_suggestions = rules_service.generate_suggestions_for_user(user.id, start_time)
        print(f"   ✅ {len(duplicate_suggestions)} nouvelle(s) suggestion(s) (devrait être 0)")
        
        if len(duplicate_suggestions) == 0:
            print("   ✅ Protection contre les doublons fonctionne !")
        else:
            print("   ⚠️  Des suggestions en double ont été créées")
    else:
        print("❌ Aucune suggestion générée")


def main():
    """Point d'entrée principal"""
    print("\n" + "="*60)
    print("🎯 DÉMONSTRATION DU MOTEUR DE RÈGLES DE SUGGESTIONS")
    print("="*60)
    
    # Configuration
    db = setup_database()
    user, categories = create_test_data(db)
    
    # Exécuter les démos
    demo_break_rule(db, user, categories)
    demo_balance_rule(db, user, categories)
    demo_move_event_rule(db, user, categories)
    demo_suggestion_lifecycle(db, user, categories)
    
    print("\n" + "="*60)
    print("✅ DÉMOS TERMINÉES")
    print("="*60)
    print("\n💡 Pour tester avec des données réelles:")
    print("   1. Exécutez: python migrate.py")
    print("   2. Démarrez l'API: python main.py")
    print("   3. Utilisez: POST /api/suggestions/generate")
    print("\n📚 Documentation complète: docs/SUGGESTIONS.md\n")


if __name__ == "__main__":
    main()

