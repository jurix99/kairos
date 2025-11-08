# 🎯 Scheduling Intelligent avec Optimisation Géographique

## 📋 Vue d'ensemble

Le système de scheduling intelligent de Kairos permet de trouver automatiquement le meilleur créneau pour un événement en tenant compte de multiples facteurs :

- ✅ **Disponibilité** : Vérification des créneaux libres
- 📍 **Lieu et déplacements** : Prise en compte des temps de trajet
- ⭐ **Priorité** : Respect de l'importance des événements
- ⏱️ **Durée** : Adaptation aux besoins temporels
- 🕐 **Contraintes horaires** : Respect des préférences ("pas après 19h", "le matin seulement")
- 🗺️ **Optimisation géographique** : Regroupement des événements proches

## 🏗️ Architecture

### Services

#### 1. TravelService

Service de calcul des temps de trajet entre deux lieux.

**Fonctionnalités :**
- Calcul du temps de trajet estimé
- Normalisation des adresses
- Cache des calculs pour performance
- Heuristiques basées sur les adresses

**Temps de trajet par défaut :**
- Même bâtiment : 5 minutes
- Même quartier : 15 minutes
- Même ville : 30 minutes
- Villes différentes : 60 minutes

#### 2. SmartSchedulerService

Service de scheduling intelligent avec optimisation géographique.

**Fonctionnalités :**
- Recherche du meilleur créneau disponible
- Détection des conflits de déplacement
- Optimisation des séquences d'événements
- Application de contraintes horaires personnalisées

### Contraintes de Temps

La classe `TimeConstraint` permet de définir des restrictions horaires :

```python
TimeConstraint(
    not_before=time(9, 0),      # Pas avant 9h
    not_after=time(19, 0),       # Pas après 19h
    morning_only=False,          # Matin uniquement (6h-12h)
    afternoon_only=False,        # Après-midi uniquement (12h-18h)
    evening_only=False           # Soir uniquement (18h-22h)
)
```

## 🚀 API Endpoints

### 1. Trouver le Meilleur Créneau

**POST** `/smart-schedule/find-best-slot`

Trouve le meilleur créneau pour un événement en considérant tous les facteurs.

**Request Body:**
```json
{
  "user_id": 1,
  "duration_minutes": 60,
  "preferred_start": "2025-11-10T14:00:00",
  "priority": "high",
  "location": "123 Main St, Paris",
  "category_id": 1,
  "not_before": "09:00",
  "not_after": "19:00",
  "morning_only": false,
  "afternoon_only": false,
  "evening_only": false,
  "search_days": 7
}
```

**Response:**
```json
{
  "success": true,
  "scheduled_time": "2025-11-10T14:00:00",
  "message": "Créneau préféré disponible",
  "travel_warnings": [],
  "conflicts": [],
  "optimization_applied": false
}
```

### 2. Détecter les Conflits de Déplacement

**POST** `/smart-schedule/detect-travel-conflicts`

Détecte les problèmes logistiques dus aux temps de trajet.

**Request Body:**
```json
{
  "user_id": 1,
  "date": "2025-11-10T00:00:00"
}
```

**Response:**
```json
{
  "date": "2025-11-10",
  "conflicts_found": 1,
  "conflicts": [
    {
      "current_event": {
        "id": 1,
        "title": "Réunion Paris",
        "end_time": "2025-11-10T11:00:00",
        "location": "Paris"
      },
      "next_event": {
        "id": 2,
        "title": "Rendez-vous Lyon",
        "start_time": "2025-11-10T11:30:00",
        "location": "Lyon",
        "is_flexible": true
      },
      "conflict": {
        "travel_time_minutes": 60,
        "shortage_minutes": 30,
        "suggested_new_time": "2025-11-10T12:00:00"
      },
      "message": "Ton trajet entre 'Paris' et 'Lyon' prend 60 min, veux-tu que je déplace 'Rendez-vous Lyon' à 12:00 ?"
    }
  ],
  "message": "1 conflit(s) de déplacement détecté(s)"
}
```

### 3. Optimiser une Séquence d'Événements

**POST** `/smart-schedule/optimize-sequence`

Optimise l'ordre des événements pour minimiser les déplacements.

**Request Body:**
```json
{
  "user_id": 1,
  "date": "2025-11-10T00:00:00",
  "minimize_travel": true
}
```

**Response:**
```json
{
  "optimization_possible": true,
  "current_travel_minutes": 90,
  "optimized_travel_minutes": 45,
  "savings_minutes": 45,
  "suggestions": [],
  "message": "Je peux réorganiser tes événements pour économiser 45 min de déplacement"
}
```

### 4. Calculer un Temps de Trajet

**POST** `/smart-schedule/calculate-travel-time`

Calcule le temps de trajet entre deux lieux.

**Request Body:**
```json
{
  "origin": "123 Main St, Paris",
  "destination": "456 Avenue, Lyon"
}
```

**Response:**
```json
{
  "origin": "123 Main St, Paris",
  "destination": "456 Avenue, Lyon",
  "travel_time_minutes": 60,
  "travel_time": "0:60:00",
  "needs_buffer": true,
  "warning_message": "Votre trajet entre '123 Main St, Paris' et '456 Avenue, Lyon' prend environ 60 min"
}
```

### 5. Analyser les Déplacements Quotidiens

**GET** `/smart-schedule/travel-analysis/{user_id}?date=2025-11-10`

Analyse complète des déplacements d'une journée avec statistiques.

**Response:**
```json
{
  "date": "2025-11-10",
  "total_events": 5,
  "events_with_location": 5,
  "total_travel_minutes": 120,
  "travel_details": [
    {
      "from_event": {
        "id": 1,
        "title": "Meeting A",
        "location": "Paris",
        "end_time": "2025-11-10T10:00:00"
      },
      "to_event": {
        "id": 2,
        "title": "Meeting B",
        "location": "Lyon",
        "start_time": "2025-11-10T11:30:00"
      },
      "travel_time_minutes": 60,
      "available_time_minutes": 90,
      "is_sufficient": true
    }
  ],
  "locations_visited": 3,
  "location_groups": {
    "Paris": [
      {"id": 1, "title": "Meeting A", "start_time": "2025-11-10T09:00:00"},
      {"id": 3, "title": "Meeting C", "start_time": "2025-11-10T15:00:00"}
    ],
    "Lyon": [
      {"id": 2, "title": "Meeting B", "start_time": "2025-11-10T11:30:00"}
    ]
  },
  "recommendations": [
    "✅ Votre organisation actuelle est optimale !"
  ]
}
```

### 6. Valider des Contraintes Horaires

**POST** `/smart-schedule/constraints/validate`

Vérifie si une heure satisfait des contraintes données.

**Request Body:**
```json
{
  "not_before": "09:00",
  "not_after": "19:00",
  "morning_only": false,
  "afternoon_only": false,
  "evening_only": false,
  "test_time": "2025-11-10T14:00:00"
}
```

**Response:**
```json
{
  "test_time": "2025-11-10T14:00:00",
  "is_valid": true,
  "reasons": ["Toutes les contraintes sont satisfaites"]
}
```

## 💡 Exemples d'Utilisation

### Exemple 1 : Planifier un Rendez-vous avec Contraintes

```python
import requests

# Trouver le meilleur créneau pour un rendez-vous
# qui doit avoir lieu le matin uniquement
response = requests.post(
    "http://localhost:8080/smart-schedule/find-best-slot",
    json={
        "user_id": 1,
        "duration_minutes": 90,
        "preferred_start": "2025-11-10T09:00:00",
        "priority": "high",
        "location": "Bureaux Paris, 10 Rue de la Paix",
        "category_id": 1,
        "morning_only": True,
        "search_days": 7
    }
)

result = response.json()
if result["success"]:
    print(f"Créneau trouvé : {result['scheduled_time']}")
    if result["travel_warnings"]:
        print("⚠️ Attention aux déplacements :")
        for warning in result["travel_warnings"]:
            print(f"  - {warning}")
```

### Exemple 2 : Vérifier et Résoudre les Conflits de Déplacement

```python
# Détecter les conflits de la journée
response = requests.post(
    "http://localhost:8080/smart-schedule/detect-travel-conflicts",
    json={
        "user_id": 1,
        "date": "2025-11-10T00:00:00"
    }
)

conflicts = response.json()
if conflicts["conflicts_found"] > 0:
    print(f"⚠️ {conflicts['conflicts_found']} conflit(s) détecté(s) :")
    for conflict in conflicts["conflicts"]:
        print(f"\n{conflict['message']}")
        print(f"  Temps de trajet nécessaire : {conflict['conflict']['travel_time_minutes']} min")
        print(f"  Nouveau créneau suggéré : {conflict['conflict']['suggested_new_time']}")
```

### Exemple 3 : Optimiser une Journée Complète

```python
# Obtenir l'analyse des déplacements
response = requests.get(
    "http://localhost:8080/smart-schedule/travel-analysis/1",
    params={"date": "2025-11-10T00:00:00"}
)

analysis = response.json()
print(f"📊 Analyse de la journée :")
print(f"  Événements : {analysis['total_events']}")
print(f"  Temps de trajet total : {analysis['total_travel_minutes']} min")
print(f"  Lieux visités : {analysis['locations_visited']}")

print("\n💡 Recommandations :")
for rec in analysis["recommendations"]:
    print(f"  {rec}")

# Optimiser si nécessaire
response = requests.post(
    "http://localhost:8080/smart-schedule/optimize-sequence",
    json={
        "user_id": 1,
        "date": "2025-11-10T00:00:00",
        "minimize_travel": True
    }
)

optimization = response.json()
if optimization["optimization_possible"]:
    savings = optimization["savings_minutes"]
    print(f"\n✨ Optimisation possible : économie de {savings} min !")
```

## 🧪 Tests

### Exécution des Tests

```bash
cd backend

# Tests du service de calcul de trajet
pytest tests/test_travel_service.py -v

# Tests du service de scheduling intelligent
pytest tests/test_smart_scheduler_service.py -v

# Tous les tests
pytest tests/test_travel_service.py tests/test_smart_scheduler_service.py -v
```

### Couverture des Tests

Les tests couvrent :
- ✅ Calcul des temps de trajet
- ✅ Normalisation des lieux
- ✅ Mécanisme de cache
- ✅ Contraintes horaires
- ✅ Détection de conflits
- ✅ Disponibilité des créneaux
- ✅ Scoring des créneaux
- ✅ Groupement par lieu

## 🔧 Configuration

### Personnalisation des Temps de Trajet

Vous pouvez personnaliser les temps de trajet par défaut dans `travel_service.py` :

```python
class TravelService:
    DEFAULT_TRAVEL_TIMES = {
        "same_building": 5,      # Minutes
        "same_neighborhood": 15,
        "same_city": 30,
        "different_city": 60,
        "unknown": 30,
    }
```

### Configuration du Scheduler

Dans `smart_scheduler_service.py`, vous pouvez ajuster :

```python
# Créneaux de recherche (toutes les 15 minutes)
current_time += timedelta(minutes=15)

# Heures de recherche par défaut
start_hour = 8  # 8h
end_hour = 20   # 20h

# Seuil pour considérer qu'un événement est "proche"
max_distance_minutes = 30

# Seuil pour l'économie minimum d'une optimisation
if savings.total_seconds() > 600:  # 10 minutes
```

## 🎯 Cas d'Usage

### 1. Planification Intelligente

L'utilisateur veut planifier une réunion mais ne sait pas quand :

1. **Entrée** : "Je dois organiser une réunion de 2h à Paris, de préférence l'après-midi"
2. **Système** :
   - Cherche les créneaux de 2h disponibles l'après-midi
   - Vérifie les temps de trajet avant/après
   - Propose le meilleur créneau
3. **Sortie** : "Le meilleur créneau est jeudi 14h-16h, avec 30 min de trajet depuis ta réunion précédente"

### 2. Détection Proactive de Problèmes

Le système détecte automatiquement les conflits :

```
⚠️ Alerte détectée :
Ton trajet entre 'Bureaux Paris' et 'Restaurant Lyon' 
prend 60 min, mais tu n'as que 30 min entre tes deux 
événements.

💡 Suggestion : Déplacer 'Déjeuner Restaurant' à 12:30 
au lieu de 12:00 ?
```

### 3. Optimisation Géographique

Pour une journée avec plusieurs événements :

```
📊 Analyse de ta journée :
- 5 événements
- 3 lieux différents
- 120 min de déplacement

💡 Je peux réorganiser pour économiser 45 min :
1. Grouper les 2 événements à Paris le matin
2. Déplacer l'événement à Lyon l'après-midi
3. Finir avec l'événement proche de chez toi
```

## 🚀 Évolutions Futures

### Phase 2 : Intégration avec APIs Externes

- [ ] Google Maps API pour temps de trajet réels
- [ ] Trafic en temps réel
- [ ] Modes de transport (voiture, transport en commun, vélo)
- [ ] Météo pour ajuster les temps de trajet

### Phase 3 : Machine Learning

- [ ] Apprentissage des temps de trajet réels de l'utilisateur
- [ ] Prédiction des retards
- [ ] Personnalisation des recommandations
- [ ] Détection de patterns

### Phase 4 : Fonctionnalités Avancées

- [ ] Multi-utilisateurs (réunions collaboratives)
- [ ] Réservation automatique de salles
- [ ] Suggestions de lieux de rencontre optimaux
- [ ] Intégration avec applications de transport

## 📚 Ressources

- **Code source** :
  - `backend/src/backend/services/travel_service.py`
  - `backend/src/backend/services/smart_scheduler_service.py`
  - `backend/src/backend/routes/smart_scheduling.py`

- **Tests** :
  - `backend/tests/test_travel_service.py`
  - `backend/tests/test_smart_scheduler_service.py`

- **Documentation API** : http://localhost:8080/docs

## 🤝 Contribution

Pour contribuer à l'amélioration du système de scheduling intelligent :

1. Créer une issue décrivant la fonctionnalité ou le bug
2. Fork le projet
3. Créer une branche (`git checkout -b feature/AmazingFeature`)
4. Commit les changements (`git commit -m 'Add AmazingFeature'`)
5. Push vers la branche (`git push origin feature/AmazingFeature`)
6. Ouvrir une Pull Request

## 📞 Support

Pour toute question ou problème :
- **Issues GitHub** : https://github.com/jurix99/kairos/issues
- **Documentation** : http://localhost:8080/docs

---

**Fait avec ❤️ par l'équipe Kairos**
