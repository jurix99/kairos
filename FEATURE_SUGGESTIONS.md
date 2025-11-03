# ✨ Feature: Moteur de Règles pour Suggestions Intelligentes

## 📋 Résumé

Implémentation complète d'un moteur de règles qui analyse le calendrier de l'utilisateur et génère automatiquement des suggestions intelligentes pour améliorer la productivité et le bien-être.

## ✅ Critères d'Acceptation

### ✓ Le moteur de règles génère des suggestions basiques

**Implémenté:** Le système génère 3 types de suggestions :

1. **💆 Prendre une pause** (`take_break`)
   - Déclenchée après 3 heures de travail continu
   - Suggère une pause de 15 minutes
   - Priorité: Medium

2. **⚖️ Équilibrer la journée** (`balance_day`)
   - Déclenchée si une catégorie > 60% du temps
   - Suggère d'équilibrer avec d'autres activités
   - Priorité: Low

3. **📅 Déplacer un événement** (`move_event`)
   - Déclenchée pour les événements fréquemment reportés
   - Suggère de replanifier ou reconsidérer la priorité
   - Priorité: Medium

### ✓ Les suggestions sont basées sur les données du calendrier

**Implémenté:** Le moteur analyse :
- Les événements de la journée (horaires, durées, catégories)
- Les blocs de travail continus (détection des pauses < 30 min)
- La répartition du temps par catégorie
- L'historique de modifications des événements

### ✓ Les suggestions sont enregistrées dans la base de données

**Implémenté:** 
- Table `suggestions` créée avec tous les champs nécessaires
- Relations avec les tables `users` et `events`
- Gestion des statuts (pending, accepted, rejected, expired)
- Système d'expiration automatique (24h par défaut)

## 🏗️ Architecture

### Modèle de Données

**Nouveau modèle:** `Suggestion`

```python
class Suggestion(Base):
    __tablename__ = "suggestions"
    
    id: int
    type: str  # take_break, balance_day, move_event
    title: str
    description: str
    priority: str  # low, medium, high
    status: str  # pending, accepted, rejected, expired
    extra_data: str  # JSON avec données supplémentaires
    rule_triggered: str  # Nom de la règle
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    user_id: int  # FK vers users
    related_event_id: int  # FK optionnelle vers events
```

### Schémas Pydantic

**Nouveaux schémas:**
- `SuggestionType` (Enum): Types de suggestions
- `SuggestionStatus` (Enum): Statuts possibles
- `SuggestionBase`: Schéma de base
- `SuggestionCreate`: Création
- `SuggestionUpdate`: Mise à jour
- `SuggestionResponse`: Réponse API

### Service Layer

**Nouveau service:** `RulesEngineService`

**Méthodes principales:**
```python
- generate_suggestions_for_user(user_id, date)
- get_active_suggestions(user_id)
- update_suggestion_status(suggestion_id, user_id, status)
- _check_break_rule(user_id, date)
- _check_balance_rule(user_id, date)
- _check_postponement_rule(user_id)
- _cleanup_expired_suggestions(user_id)
```

### Routes API

**Nouvelles routes:** `/api/suggestions`

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/suggestions/` | Liste les suggestions (avec filtre statut) |
| GET | `/api/suggestions/{id}` | Récupère une suggestion |
| POST | `/api/suggestions/generate` | Génère de nouvelles suggestions |
| PATCH | `/api/suggestions/{id}` | Met à jour le statut |
| DELETE | `/api/suggestions/{id}` | Supprime (rejette) une suggestion |

## 📁 Fichiers Créés/Modifiés

### Nouveaux Fichiers

1. **`backend/src/backend/models/database.py`** ✏️
   - Ajout du modèle `Suggestion`

2. **`backend/src/backend/models/schemas.py`** ✏️
   - Ajout des schémas pour les suggestions

3. **`backend/src/backend/services/rules_engine_service.py`** ✨ NOUVEAU
   - Service complet du moteur de règles
   - ~400 lignes de code
   - 3 règles implémentées
   - Gestion de l'expiration

4. **`backend/src/backend/routes/suggestions.py`** ✨ NOUVEAU
   - Routes API complètes
   - 5 endpoints
   - Authentification requise

5. **`docs/SUGGESTIONS.md`** ✨ NOUVEAU
   - Documentation complète
   - Guide d'utilisation
   - Exemples d'API
   - Architecture détaillée

6. **`backend/tests/test_rules_engine.py`** ✨ NOUVEAU
   - Tests unitaires complets
   - 7 tests couvrant tous les cas
   - Test de non-duplication
   - Test d'expiration

7. **`FEATURE_SUGGESTIONS.md`** ✨ NOUVEAU (ce fichier)
   - Récapitulatif de la feature

### Fichiers Modifiés

8. **`backend/src/backend/routes/__init__.py`** ✏️
   - Ajout de `suggestions_router`

9. **`backend/src/backend/app.py`** ✏️
   - Inclusion du router suggestions

10. **`backend/migrate.py`** ✏️
    - Import du modèle `Suggestion`

## 🧪 Tests

### Tests Unitaires

7 tests créés couvrant :
- ✅ Déclenchement de la règle de pause
- ✅ Déclenchement de la règle d'équilibrage
- ✅ Déclenchement de la règle de déplacement
- ✅ Non-duplication des suggestions
- ✅ Expiration automatique
- ✅ Mise à jour du statut
- ✅ Récupération des suggestions actives

### Exécution des Tests

```bash
cd backend
pytest tests/test_rules_engine.py -v
```

## 🚀 Utilisation

### 1. Migration de la Base de Données

```bash
cd backend
python migrate.py
```

Cela créera la table `suggestions` dans la base de données.

### 2. Démarrer le Backend

```bash
cd backend
python main.py
```

### 3. Générer des Suggestions

**Via l'API:**

```bash
curl -X POST http://localhost:8000/api/suggestions/generate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Via le code:**

```python
from backend.services.rules_engine_service import RulesEngineService

rules_service = RulesEngineService(db)
suggestions = rules_service.generate_suggestions_for_user(user_id=1)
```

### 4. Récupérer les Suggestions

```bash
curl http://localhost:8000/api/suggestions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Accepter/Rejeter une Suggestion

```bash
curl -X PATCH http://localhost:8000/api/suggestions/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

## 📊 Exemples de Suggestions Générées

### Exemple 1: Pause Recommandée

**Scénario:** Utilisateur avec 4h de travail continu

```json
{
  "id": 1,
  "type": "take_break",
  "title": "💆 Temps de pause recommandé",
  "description": "Vous avez travaillé 4.0 heures consécutives. Il est recommandé de prendre une pause de 15 minutes pour maintenir votre productivité et votre bien-être.",
  "priority": "medium",
  "status": "pending",
  "extra_data": "{\"hours_worked\": 4.0, \"suggested_break_duration\": 15}",
  "rule_triggered": "break_after_work_hours",
  "created_at": "2025-11-03T14:30:00",
  "expires_at": "2025-11-04T14:30:00",
  "user_id": 1
}
```

### Exemple 2: Rééquilibrage

**Scénario:** 75% du temps en "Travail"

```json
{
  "id": 2,
  "type": "balance_day",
  "title": "⚖️ Rééquilibrer votre journée",
  "description": "Votre journée est fortement orientée vers 'Travail' (75.0% de votre temps). Pensez à équilibrer avec Personnel, Loisirs, Santé pour une meilleure harmonie.",
  "priority": "low",
  "status": "pending",
  "extra_data": "{\"dominant_category\": \"Travail\", \"percentage\": 75.0, \"category_distribution\": {\"Travail\": 6.0, \"Personnel\": 1.5, \"Loisirs\": 0.5}}",
  "rule_triggered": "balance_day_categories",
  "created_at": "2025-11-03T14:30:00",
  "expires_at": "2025-11-04T14:30:00",
  "user_id": 1
}
```

### Exemple 3: Événement à Replanifier

**Scénario:** Événement reporté plusieurs fois

```json
{
  "id": 3,
  "type": "move_event",
  "title": "📅 Événement à replanifier",
  "description": "L'événement 'Révision du budget' a été reporté plusieurs fois. Il serait peut-être temps de le replanifier à une date plus adaptée ou de reconsidérer sa priorité.",
  "priority": "medium",
  "status": "pending",
  "extra_data": "{\"event_id\": 42, \"event_title\": \"Révision du budget\", \"current_start_time\": \"2025-11-05T10:00:00\", \"times_modified\": \"multiple\"}",
  "rule_triggered": "frequent_postponement",
  "related_event_id": 42,
  "created_at": "2025-11-03T14:30:00",
  "expires_at": "2025-11-04T14:30:00",
  "user_id": 1
}
```

## 🎯 Configurations

Les constantes du moteur peuvent être ajustées dans `rules_engine_service.py`:

```python
class RulesEngineService:
    # Constantes configurables
    MAX_WORK_HOURS_BEFORE_BREAK = 3.0      # Heures avant pause
    BREAK_DURATION_MINUTES = 15            # Durée de pause
    IMBALANCE_THRESHOLD = 0.4              # Seuil déséquilibre (40%)
    POSTPONEMENT_THRESHOLD = 3             # Nombre de reports
    SUGGESTION_EXPIRY_HOURS = 24           # Durée de vie
```

## 🔄 Workflow Typique

1. **Génération Automatique**
   - L'utilisateur utilise son calendrier normalement
   - Le système peut générer des suggestions manuellement ou automatiquement

2. **Affichage**
   - Les suggestions actives sont récupérées via l'API
   - Elles sont affichées dans l'interface utilisateur

3. **Interaction**
   - L'utilisateur accepte ou rejette les suggestions
   - Le statut est mis à jour dans la base de données

4. **Expiration**
   - Les suggestions non traitées expirent après 24h
   - Elles sont automatiquement marquées comme "expired"

5. **Nettoyage**
   - Le système nettoie les suggestions expirées automatiquement
   - Lors de chaque requête, les suggestions expirées sont marquées

## 🎨 Intégration Frontend (À Faire)

Pour intégrer avec le frontend Next.js :

### 1. Créer le Service API

```typescript
// frontend/lib/api.ts
export async function getSuggestions(status?: string) {
  const response = await fetch(
    `/api/suggestions/${status ? `?status=${status}` : ''}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.json();
}

export async function generateSuggestions() {
  const response = await fetch('/api/suggestions/generate', {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.json();
}

export async function updateSuggestionStatus(id: number, status: string) {
  const response = await fetch(`/api/suggestions/${id}`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status })
  });
  return response.json();
}
```

### 2. Créer le Composant Suggestions

```typescript
// frontend/components/suggestions-panel.tsx
export function SuggestionsPanel() {
  const [suggestions, setSuggestions] = useState([]);
  
  useEffect(() => {
    getSuggestions('pending').then(setSuggestions);
  }, []);
  
  const handleAccept = async (id: number) => {
    await updateSuggestionStatus(id, 'accepted');
    // Rafraîchir la liste
  };
  
  const handleReject = async (id: number) => {
    await updateSuggestionStatus(id, 'rejected');
    // Rafraîchir la liste
  };
  
  return (
    <div className="suggestions-panel">
      {suggestions.map(suggestion => (
        <SuggestionCard
          key={suggestion.id}
          suggestion={suggestion}
          onAccept={() => handleAccept(suggestion.id)}
          onReject={() => handleReject(suggestion.id)}
        />
      ))}
    </div>
  );
}
```

### 3. Ajouter au Dashboard

```typescript
// frontend/app/dashboard/page.tsx
import { SuggestionsPanel } from '@/components/suggestions-panel';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <SuggestionsPanel />
      {/* Autres composants */}
    </div>
  );
}
```

## 📈 Métriques et Analyse

Le système peut être étendu pour tracker :
- Taux d'acceptation des suggestions par type
- Temps moyen avant action sur une suggestion
- Corrélation entre suggestions et productivité
- Patterns de comportement utilisateur

## 🔮 Évolutions Futures

### Phase 2: Suggestions Avancées
- Suggestion de priorisation (tâches urgentes négligées)
- Suggestion de temps libre (créneaux pour loisirs)
- Suggestion d'optimisation (réorganiser les événements)

### Phase 3: Machine Learning
- Apprentissage des préférences utilisateur
- Personnalisation des seuils de déclenchement
- Prédiction des conflits

### Phase 4: Notifications
- Notifications push en temps réel
- Emails récapitulatifs quotidiens
- Intégration WebSocket

## 📚 Documentation

- **Guide complet:** `docs/SUGGESTIONS.md`
- **Tests:** `backend/tests/test_rules_engine.py`
- **API:** Swagger UI à `http://localhost:8000/docs`

## 🎉 Conclusion

Le moteur de règles pour suggestions intelligentes est **entièrement implémenté** et répond à tous les critères d'acceptation du MVP :

✅ Génère des suggestions basiques (3 types)  
✅ Basé sur les données du calendrier  
✅ Enregistre dans la base de données  
✅ API complète avec authentification  
✅ Tests unitaires couvrant tous les cas  
✅ Documentation détaillée  

Le système est prêt pour l'intégration frontend et peut être étendu avec de nouvelles règles facilement.

