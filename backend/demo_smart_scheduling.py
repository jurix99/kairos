#!/usr/bin/env python3
"""
Script de démonstration du système de scheduling intelligent avec optimisation géographique

Ce script montre comment utiliser les nouvelles fonctionnalités :
- Calcul des temps de trajet
- Recherche du meilleur créneau
- Détection des conflits de déplacement
- Optimisation géographique des événements
"""

from datetime import datetime, timedelta, time
from backend.services.travel_service import TravelService
from backend.services.smart_scheduler_service import (
    TimeConstraint,
    SmartSchedulerService
)


def demo_travel_service():
    """Démonstration du service de calcul des temps de trajet"""
    print("=" * 70)
    print("DÉMONSTRATION : Service de Calcul des Temps de Trajet")
    print("=" * 70)
    
    locations = [
        ("Bureaux Paris, 10 Rue de la Paix", "Restaurant Paris, 15 Rue Montmartre"),
        ("Paris, France", "Lyon, France"),
        ("123 Main St, Bureau 101, Paris", "123 Main St, Bureau 205, Paris"),
        ("10 Rue A, 5ème arrondissement, Paris", "25 Rue B, 5ème arrondissement, Paris"),
    ]
    
    for origin, destination in locations:
        print(f"\n📍 Trajet : {origin}")
        print(f"   → {destination}")
        
        info = TravelService.get_travel_info(origin, destination)
        print(f"   ⏱️  Temps estimé : {info['travel_time_minutes']} minutes")
        
        if info['warning_message']:
            print(f"   ⚠️  {info['warning_message']}")
        else:
            print(f"   ✅ Pas de déplacement significatif")
    
    print("\n" + "=" * 70)


def demo_time_constraints():
    """Démonstration des contraintes horaires"""
    print("\n" + "=" * 70)
    print("DÉMONSTRATION : Contraintes Horaires")
    print("=" * 70)
    
    # Test 1 : Matin seulement
    print("\n📋 Contrainte : Matin seulement (6h-12h)")
    constraint = TimeConstraint(morning_only=True)
    
    test_times = [
        datetime(2025, 11, 10, 9, 0),   # 9h - valide
        datetime(2025, 11, 10, 14, 0),  # 14h - invalide
    ]
    
    for dt in test_times:
        is_valid = constraint.is_valid_time(dt)
        status = "✅ Valide" if is_valid else "❌ Invalide"
        print(f"   {dt.strftime('%H:%M')} - {status}")
    
    # Test 2 : Pas après 19h
    print("\n📋 Contrainte : Pas après 19h00")
    constraint = TimeConstraint(not_after=time(19, 0))
    
    test_times = [
        datetime(2025, 11, 10, 18, 0),  # 18h - valide
        datetime(2025, 11, 10, 20, 0),  # 20h - invalide
    ]
    
    for dt in test_times:
        is_valid = constraint.is_valid_time(dt)
        status = "✅ Valide" if is_valid else "❌ Invalide"
        print(f"   {dt.strftime('%H:%M')} - {status}")
    
    # Test 3 : Plage horaire
    print("\n📋 Contrainte : Entre 9h et 18h")
    constraint = TimeConstraint(
        not_before=time(9, 0),
        not_after=time(18, 0)
    )
    
    test_times = [
        datetime(2025, 11, 10, 8, 0),   # 8h - invalide
        datetime(2025, 11, 10, 12, 0),  # 12h - valide
        datetime(2025, 11, 10, 19, 0),  # 19h - invalide
    ]
    
    for dt in test_times:
        is_valid = constraint.is_valid_time(dt)
        status = "✅ Valide" if is_valid else "❌ Invalide"
        print(f"   {dt.strftime('%H:%M')} - {status}")
    
    print("\n" + "=" * 70)


def demo_conflict_detection():
    """Démonstration de la détection de conflits"""
    print("\n" + "=" * 70)
    print("DÉMONSTRATION : Détection de Conflits de Déplacement")
    print("=" * 70)
    
    # Simuler deux événements avec temps de trajet insuffisant
    print("\n📅 Scénario : Deux événements dans des villes différentes")
    print("   Événement 1 : Réunion à Paris, 10h-11h")
    print("   Événement 2 : Déjeuner à Lyon, 11h30-13h")
    
    # Calculer le temps de trajet
    travel_time = TravelService.calculate_travel_time("Paris, France", "Lyon, France")
    available_time = timedelta(minutes=30)  # 11h à 11h30
    
    print(f"\n   ⏱️  Temps de trajet nécessaire : {int(travel_time.total_seconds() / 60)} min")
    print(f"   ⏱️  Temps disponible : {int(available_time.total_seconds() / 60)} min")
    
    if travel_time > available_time:
        shortage = travel_time - available_time
        print(f"\n   ⚠️  CONFLIT DÉTECTÉ !")
        print(f"   ❌ Temps insuffisant de {int(shortage.total_seconds() / 60)} min")
        
        suggested_time = datetime(2025, 11, 10, 11, 0) + travel_time
        print(f"\n   💡 Suggestion : Déplacer le déjeuner à {suggested_time.strftime('%H:%M')}")
    
    print("\n" + "=" * 70)


def demo_geographic_optimization():
    """Démonstration de l'optimisation géographique"""
    print("\n" + "=" * 70)
    print("DÉMONSTRATION : Optimisation Géographique")
    print("=" * 70)
    
    # Simuler une journée avec plusieurs événements
    events = [
        {"title": "Réunion A", "location": "Paris", "time": "09:00"},
        {"title": "Déjeuner", "location": "Lyon", "time": "12:00"},
        {"title": "Réunion B", "location": "Paris", "time": "14:00"},
        {"title": "Conférence", "location": "Lyon", "time": "16:00"},
    ]
    
    print("\n📅 Planning actuel (non optimisé) :")
    for event in events:
        print(f"   {event['time']} - {event['title']} ({event['location']})")
    
    # Calculer le temps de trajet total
    total_travel = timedelta(0)
    for i in range(len(events) - 1):
        travel = TravelService.calculate_travel_time(
            events[i]['location'], events[i + 1]['location']
        )
        total_travel += travel
        
        if travel.total_seconds() > 0:
            print(f"      └─> Trajet vers {events[i + 1]['title']} : {int(travel.total_seconds() / 60)} min")
    
    print(f"\n   ⏱️  Temps de trajet total : {int(total_travel.total_seconds() / 60)} min")
    
    # Proposer une optimisation
    print("\n📅 Planning optimisé (groupé par lieu) :")
    optimized = [
        {"title": "Réunion A", "location": "Paris", "time": "09:00"},
        {"title": "Réunion B", "location": "Paris", "time": "11:00"},
        {"title": "Déjeuner", "location": "Lyon", "time": "13:00"},
        {"title": "Conférence", "location": "Lyon", "time": "15:00"},
    ]
    
    for event in optimized:
        print(f"   {event['time']} - {event['title']} ({event['location']})")
    
    # Calculer le nouveau temps de trajet
    optimized_travel = timedelta(0)
    for i in range(len(optimized) - 1):
        travel = TravelService.calculate_travel_time(
            optimized[i]['location'], optimized[i + 1]['location']
        )
        optimized_travel += travel
        
        if travel.total_seconds() > 0:
            print(f"      └─> Trajet vers {optimized[i + 1]['title']} : {int(travel.total_seconds() / 60)} min")
    
    print(f"\n   ⏱️  Temps de trajet total : {int(optimized_travel.total_seconds() / 60)} min")
    
    savings = total_travel - optimized_travel
    if savings.total_seconds() > 0:
        print(f"\n   ✨ Économie de temps : {int(savings.total_seconds() / 60)} min !")
    
    print("\n" + "=" * 70)


def main():
    """Point d'entrée principal"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🚀 KAIROS - Démonstration du Scheduling Intelligent  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Exécuter les démonstrations
    demo_travel_service()
    demo_time_constraints()
    demo_conflict_detection()
    demo_geographic_optimization()
    
    # Résumé
    print("\n" + "=" * 70)
    print("RÉSUMÉ DES FONCTIONNALITÉS")
    print("=" * 70)
    print("""
✅ Calcul automatique des temps de trajet
✅ Contraintes horaires personnalisées  
✅ Détection proactive des conflits de déplacement
✅ Optimisation géographique des événements
✅ Suggestions intelligentes de réorganisation

📚 Documentation complète : docs/SMART_SCHEDULING.md
🌐 API Interactive : http://localhost:8080/docs
    """)


if __name__ == "__main__":
    main()
