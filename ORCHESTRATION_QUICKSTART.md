# 🎯 Guide Rapide : Système d'Orchestration Multi-Agents

## Vue d'Ensemble

Le système d'orchestration multi-agents de Kairos transforme vos demandes en plans d'action structurés grâce à une intelligence artificielle spécialisée.

## 🚀 Démarrage Rapide

### Installation

```bash
cd backend
pip install -e .
```

### Configuration

Créez un fichier `.env` à la racine :

```env
# Optionnel : Pour des réponses IA avancées
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Base de données
DATABASE_URL=sqlite:///./kairos.db
```

> **Note** : Le système fonctionne même sans OpenAI (mode fallback avec règles prédéfinies)

### Lancer le Serveur

```bash
cd backend
python3 main.py
```

Le serveur démarre sur `http://localhost:8080`

### Documentation Interactive

Accédez à la documentation Swagger : `http://localhost:8080/docs`

## 📝 Exemples d'Utilisation

### 1. Via l'API

#### Classification d'un Besoin

```bash
curl -X POST http://localhost:8080/api/orchestration/classify \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Je veux apprendre le piano"
  }'
```

**Réponse** :
```json
{
  "need_type": "habit_skill",
  "complexity": "moderate",
  "suggested_agents": ["coach", "planner"],
  "confidence": 0.92,
  "reasoning": "Apprentissage d'une compétence nécessitant progression graduelle",
  "key_characteristics": ["Développement progressif", "Long terme"]
}
```

#### Plan Orchestré Complet

```bash
curl -X POST http://localhost:8080/api/orchestration/plan \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_input": "Créer une startup tech",
    "create_goals": true
  }'
```

### 2. Via le Script de Démonstration

```bash
python3 demo_orchestration.py
```

Ce script interactif vous permet de tester différents types de besoins.

### 3. Dans Votre Code Python

```python
from backend.services.orchestration_service import OrchestrationService
from backend.models.schemas import OrchestratedPlanRequest

# Initialiser le service
orchestration = OrchestrationService(db_session)

# Créer un plan
request = OrchestratedPlanRequest(
    user_input="Courir un marathon en 6 mois",
    create_goals=True
)

response = await orchestration.create_orchestrated_plan(
    request,
    user_id=user.id
)

# Exploiter les résultats
print(f"Type: {response.classification.need_type}")
print(f"Agents utilisés: {len(response.agent_responses)}")
print(f"Objectifs créés: {response.created_goals}")
print(f"Résumé: {response.summary}")
```

## 🎯 Types de Besoins Supportés

| Type | Description | Exemple | Agents |
|------|-------------|---------|--------|
| **Tâche Ponctuelle** | Action simple, court terme | "Réserver un restaurant" | Exécutif |
| **Habitude/Compétence** | Développement long terme | "Apprendre l'italien" | Coach + Planificateur |
| **Projet Complexe** | Multi-phases, ressources | "Créer une entreprise" | Stratège + Planificateur + Ressources + Exécutif |
| **Décision/Recherche** | Comparaison d'options | "Choisir une assurance" | Recherche |
| **Événement Social** | Organisation logistique | "Organiser un mariage" | Social + Planificateur |

## 🤖 Agents Disponibles

### 🎯 Agent Exécutif
Génère des étapes d'action pour les tâches simples

**Exemple** :
```
Input: "Acheter un cadeau"
Output:
  - Définir le budget
  - Identifier les goûts de la personne
  - Rechercher des idées
  - Acheter et emballer
```

### 🏃 Agent Coach
Crée des plans progressifs pour les habitudes et compétences

**Exemple** :
```
Input: "Courir un marathon"
Output:
  Phase 1 (Semaines 1-4): Base - 3x/semaine, 3-5km
  Phase 2 (Semaines 5-12): Développement - 4x/semaine, 8-12km
  Phase 3 (Semaines 13-20): Intensif - 5x/semaine, 15-25km
```

### 🎯 Agent Stratège
Définit les grandes phases d'un projet

**Exemple** :
```
Input: "Créer une entreprise"
Output:
  Phase 1: Validation (4 semaines)
  Phase 2: Création juridique (2 semaines)
  Phase 3: Développement produit (12 semaines)
  Phase 4: Lancement (4 semaines)
```

### 📅 Agent Planificateur
Crée un planning détaillé avec dates

### 💰 Agent Ressources
Identifie budget, outils, compétences nécessaires

### 🔍 Agent Recherche
Compare et recommande des options

### 🎉 Agent Social
Planifie les événements sociaux

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     UTILISATEUR                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  NIVEAU 1: CLASSIFICATION                    │
│                                                               │
│  Input: "Je veux apprendre le piano"                        │
│  → Analyse et catégorisation                                │
│  → Type: habit_skill                                        │
│  → Agents suggérés: [coach, planner]                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              NIVEAU 2: ORCHESTRATION D'AGENTS                │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Agent Coach │  │ Agent        │  │ Agent        │       │
│  │             │  │ Planificateur│  │ Ressources   │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  Exécution parallèle des agents appropriés                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTÉGRATION                               │
│                                                               │
│  • Consolidation des résultats                              │
│  • Création d'objectifs/événements                          │
│  • Génération du résumé                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  PLAN STRUCTURÉ                              │
│                                                               │
│  • Classification                                            │
│  • Résultats des agents                                     │
│  • Plan intégré                                              │
│  • Prochaines étapes                                        │
│  • Objectifs créés                                           │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Personnalisation

### Ajouter un Nouveau Type de Besoin

1. Ajouter dans `models/schemas.py` :
```python
class NeedType(str, Enum):
    # ...
    NEW_TYPE = "new_type"
```

2. Ajouter les mots-clés dans `need_classifier_service.py` :
```python
self.keywords_map = {
    NeedType.NEW_TYPE: ['keyword1', 'keyword2', ...]
}
```

3. Définir les agents associés :
```python
agent_mapping = {
    NeedType.NEW_TYPE: [AgentType.AGENT1, AgentType.AGENT2]
}
```

### Ajouter un Nouvel Agent

1. Créer la méthode dans `multi_agent_orchestrator_service.py` :
```python
async def _execute_new_agent(self, request, user_id):
    # Logique de l'agent
    return AgentTaskResponse(...)
```

2. Ajouter dans le router :
```python
elif request.agent_type == AgentType.NEW_AGENT:
    return await self._execute_new_agent(request, user_id)
```

## 🧪 Tests

```bash
cd backend
pytest tests/test_orchestration.py -v
```

Tests disponibles :
- Classification de chaque type de besoin
- Exécution de chaque agent (mode fallback)
- Orchestration complète
- Création d'objectifs
- Intégration des résultats

## 📚 Documentation Complète

- **API** : `http://localhost:8080/docs`
- **Guide détaillé** : [`docs/ORCHESTRATION.md`](../docs/ORCHESTRATION.md)
- **Architecture** : Voir diagrammes dans la documentation

## 🐛 Dépannage

### Erreur "OpenAI not configured"

Le système fonctionne sans OpenAI en mode fallback. Pour activer OpenAI :
```bash
export OPENAI_API_KEY=sk-...
```

### Erreur d'authentification

Les endpoints protégés nécessitent un token :
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" ...
```

### Base de données verrouillée

Si SQLite est verrouillé :
```bash
rm kairos.db
python3 migrate.py
```

## 💡 Conseils d'Utilisation

### Soyez Spécifique

❌ Mauvais : "Je veux faire du sport"
✅ Bon : "Je veux courir un marathon en 6 mois"

### Ajoutez du Contexte

```json
{
  "user_input": "Apprendre le piano",
  "context": {
    "available_time": "30min par jour",
    "budget": "100€ par mois"
  }
}
```

### Exploitez les Objectifs Créés

Le système crée automatiquement des objectifs dans la base de données :
```bash
curl http://localhost:8080/goals
```

## 🚀 Prochaines Étapes

1. **Tester le système** avec vos propres demandes
2. **Explorer la documentation** API complète
3. **Intégrer** dans votre application frontend
4. **Personnaliser** les agents selon vos besoins
5. **Contribuer** en ajoutant de nouveaux agents ou types de besoins

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/jurix99/kairos/issues)
- **Documentation** : [`docs/ORCHESTRATION.md`](../docs/ORCHESTRATION.md)
- **API Docs** : `http://localhost:8080/docs`

---

Made with ❤️ by the Kairos team
