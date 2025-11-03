# Système de Suggestions Intelligentes

## Vue d'ensemble

Le moteur de règles de Kairos analyse automatiquement votre calendrier et génère des suggestions intelligentes pour améliorer votre productivité et votre bien-être.

## Types de Suggestions

### 1. 💆 Suggestion de Pause (`take_break`)

**Déclencheur:** Après 3 heures de travail continu

**Description:** Le système détecte les blocs de travail prolongés et suggère de prendre une pause de 15 minutes pour maintenir la productivité et le bien-être.

**Critères:**
- Analyse les événements de la journée
- Identifie les blocs de travail avec moins de 30 minutes d'écart entre les événements
- Génère une suggestion si le bloc dépasse 3 heures

**Exemple de suggestion:**
```json
{
  "type": "take_break",
  "title": "💆 Temps de pause recommandé",
  "description": "Vous avez travaillé 3.5 heures consécutives. Il est recommandé de prendre une pause de 15 minutes pour maintenir votre productivité et votre bien-être.",
  "priority": "medium",
  "extra_data": {
    "hours_worked": 3.5,
    "suggested_break_duration": 15
  }
}
```

### 2. ⚖️ Suggestion d'Équilibrage (`balance_day`)

**Déclencheur:** Une catégorie représente plus de 60% de la journée

**Description:** Le système détecte les déséquilibres dans la répartition du temps et suggère d'équilibrer avec d'autres activités.

**Critères:**
- Analyse la répartition du temps par catégorie
- Calcule les pourcentages de chaque catégorie
- Génère une suggestion si une catégorie dépasse 60%

**Exemple de suggestion:**
```json
{
  "type": "balance_day",
  "title": "⚖️ Rééquilibrer votre journée",
  "description": "Votre journée est fortement orientée vers 'Travail' (75.0% de votre temps). Pensez à équilibrer avec Personnel, Loisirs, Santé pour une meilleure harmonie.",
  "priority": "low",
  "extra_data": {
    "dominant_category": "Travail",
    "percentage": 75.0,
    "category_distribution": {
      "Travail": 6.0,
      "Personnel": 1.0,
      "Loisirs": 1.0
    }
  }
}
```

### 3. 📅 Suggestion de Déplacement (`move_event`)

**Déclencheur:** Un événement flexible a été reporté plusieurs fois

**Description:** Le système identifie les événements fréquemment reportés et suggère de les replanifier ou reconsidérer leur priorité.

**Critères:**
- Analyse les événements modifiés récemment (dernière semaine)
- Détecte les événements avec un écart significatif entre création et dernière modification
- Génère une suggestion pour les événements flexibles

**Exemple de suggestion:**
```json
{
  "type": "move_event",
  "title": "📅 Événement à replanifier",
  "description": "L'événement 'Révision du budget' a été reporté plusieurs fois. Il serait peut-être temps de le replanifier à une date plus adaptée ou de reconsidérer sa priorité.",
  "priority": "medium",
  "extra_data": {
    "event_id": 42,
    "event_title": "Révision du budget",
    "times_modified": "multiple"
  }
}
```

## API Endpoints

### Récupérer les suggestions actives

```http
GET /api/suggestions/
```

**Paramètres de requête:**
- `status` (optionnel): Filtrer par statut (`pending`, `accepted`, `rejected`, `expired`)

**Réponse:**
```json
[
  {
    "id": 1,
    "type": "take_break",
    "title": "💆 Temps de pause recommandé",
    "description": "...",
    "priority": "medium",
    "status": "pending",
    "created_at": "2025-11-03T14:30:00",
    "expires_at": "2025-11-04T14:30:00",
    "user_id": 1
  }
]
```

### Générer de nouvelles suggestions

```http
POST /api/suggestions/generate
```

**Paramètres de requête:**
- `date` (optionnel): Date pour laquelle générer les suggestions (format ISO 8601)

**Réponse:** Liste des suggestions générées

### Mettre à jour une suggestion

```http
PATCH /api/suggestions/{suggestion_id}
```

**Corps de la requête:**
```json
{
  "status": "accepted"
}
```

**Statuts disponibles:**
- `pending`: En attente
- `accepted`: Acceptée
- `rejected`: Rejetée
- `expired`: Expirée

### Supprimer une suggestion

```http
DELETE /api/suggestions/{suggestion_id}
```

Marque la suggestion comme rejetée.

## Configuration

Les constantes du moteur de règles peuvent être modifiées dans `rules_engine_service.py`:

```python
MAX_WORK_HOURS_BEFORE_BREAK = 3.0  # Heures de travail avant suggestion de pause
BREAK_DURATION_MINUTES = 15        # Durée de pause suggérée
IMBALANCE_THRESHOLD = 0.4          # Seuil de déséquilibre (40%)
POSTPONEMENT_THRESHOLD = 3         # Nombre de reports avant suggestion
SUGGESTION_EXPIRY_HOURS = 24      # Durée de vie d'une suggestion
```

## Nettoyage Automatique

Le système nettoie automatiquement les suggestions expirées:
- Les suggestions ont une durée de vie de 24 heures par défaut
- Lors de chaque requête, les suggestions expirées sont marquées comme `expired`
- Les suggestions expirées ne sont plus affichées dans les suggestions actives

## Architecture

### Modèle de Base de Données

```sql
CREATE TABLE suggestions (
    id INTEGER PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(10) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    extra_data TEXT,
    rule_triggered VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    user_id INTEGER NOT NULL,
    related_event_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (related_event_id) REFERENCES events(id)
);
```

### Service Layer

Le `RulesEngineService` contient toute la logique métier:
- `generate_suggestions_for_user()`: Génère toutes les suggestions pour un utilisateur
- `_check_break_rule()`: Vérifie la règle de pause
- `_check_balance_rule()`: Vérifie la règle d'équilibrage
- `_check_postponement_rule()`: Vérifie la règle de déplacement
- `get_active_suggestions()`: Récupère les suggestions actives
- `update_suggestion_status()`: Met à jour le statut d'une suggestion

## Exemples d'Utilisation

### Génération Automatique

Le système peut être configuré pour générer automatiquement des suggestions:

```python
from backend.services.rules_engine_service import RulesEngineService

# Générer les suggestions pour un utilisateur
rules_service = RulesEngineService(db)
suggestions = rules_service.generate_suggestions_for_user(user_id=1)
```

### Intégration avec un Cron Job

Vous pouvez créer un job planifié pour générer les suggestions quotidiennement:

```python
# cron_jobs/daily_suggestions.py
import schedule
import time
from datetime import datetime

def generate_daily_suggestions():
    """Génère les suggestions pour tous les utilisateurs actifs"""
    users = db.query(User).all()
    for user in users:
        rules_service = RulesEngineService(db)
        rules_service.generate_suggestions_for_user(user.id, datetime.now())

# Exécuter tous les jours à 8h00
schedule.every().day.at("08:00").do(generate_daily_suggestions)
```

## Évolutions Futures

### Suggestions Avancées
- **Suggestion de priorisation**: Identifier les tâches urgentes négligées
- **Suggestion de temps libre**: Détecter les créneaux disponibles pour les loisirs
- **Suggestion de synchronisation**: Optimiser l'ordre des événements

### Machine Learning
- Apprendre des préférences utilisateur (suggestions acceptées/rejetées)
- Personnaliser les seuils de déclenchement
- Prédire les conflits potentiels

### Notifications
- Intégrer avec un système de notifications push
- Envoyer des suggestions par email
- Notifications en temps réel via WebSocket

## Tests

Pour tester le moteur de règles:

```bash
# Lancer les tests unitaires
pytest backend/tests/test_rules_engine.py

# Test manuel via l'API
curl -X POST http://localhost:8000/api/suggestions/generate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Contribution

Pour ajouter une nouvelle règle:

1. Créer une méthode `_check_new_rule()` dans `RulesEngineService`
2. Ajouter le type de suggestion dans `SuggestionType` (schemas.py)
3. Appeler la nouvelle règle dans `generate_suggestions_for_user()`
4. Créer des tests pour la nouvelle règle
5. Documenter la règle dans ce fichier

