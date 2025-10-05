# Kairos Backend - Agenda Intelligent

Backend Python pour un agenda intelligent avec scheduling automatique et détection de conflits.

## 🚀 Fonctionnalités

### ✅ Implémentées

- **Gestion des événements** : Création, lecture, mise à jour, suppression (CRUD complet)
- **Catégories personnalisables** : Travail, Perso, Sport, Repos avec codes couleur
- **Système de priorités** : Haute, Moyenne, Basse
- **Scheduling automatique** : Placement intelligent des événements
- **Détection de conflits** : Identification et résolution des chevauchements
- **Planning quotidien/hebdomadaire** : Visualisation du planning
- **API REST complète** : Documentation automatique avec FastAPI

### 🎯 Caractéristiques techniques

- **Framework** : FastAPI pour l'API REST
- **Base de données** : SQLite avec SQLAlchemy ORM
- **Validation** : Pydantic pour la validation des données
- **Tests** : Pytest pour les tests unitaires
- **Gestion des dépendances** : uv pour un environnement Python moderne

## 📦 Installation

### Prérequis

- Python 3.11+
- uv (gestionnaire de paquets Python moderne)

### Installation avec uv

```bash
# Cloner le projet
git clone <repository-url>
cd kairos-backend

# Installer les dépendances
uv sync --dev

# Activer l'environnement virtuel
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows
```

## 🚀 Démarrage

### Lancement du serveur

```bash
# Méthode 1: Avec uv
uv run python main.py

# Méthode 2: Directement avec Python
python main.py

# Méthode 3: Avec uvicorn
uvicorn src.kairos_backend.api:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur : http://localhost:8000

### Documentation API

Une fois le serveur lancé, accédez à :
- **Documentation interactive** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc

## 📋 API Endpoints

### Catégories

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/categories` | Liste toutes les catégories |
| POST | `/categories` | Crée une nouvelle catégorie |
| GET | `/categories/{id}` | Récupère une catégorie |
| PUT | `/categories/{id}` | Met à jour une catégorie |
| DELETE | `/categories/{id}` | Supprime une catégorie |

### Événements

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/events` | Liste les événements (avec filtres) |
| POST | `/events` | Crée un nouvel événement |
| POST | `/events/schedule` | Planifie automatiquement un événement |
| GET | `/events/{id}` | Récupère un événement |
| PUT | `/events/{id}` | Met à jour un événement |
| DELETE | `/events/{id}` | Supprime un événement |

### Planning

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/schedule/daily` | Planning d'une journée |
| GET | `/schedule/weekly` | Planning d'une semaine |
| POST | `/conflicts/resolve` | Résout un conflit |

### Santé

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Vérification de l'état de l'API |

## 💡 Exemples d'utilisation

### Créer une catégorie

```bash
curl -X POST "http://localhost:8000/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rendez-vous",
    "color_code": "#FF6B6B",
    "description": "Rendez-vous médicaux et personnels"
  }'
```

### Créer un événement

```bash
curl -X POST "http://localhost:8000/events" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Réunion équipe",
    "description": "Réunion hebdomadaire de l'\''équipe",
    "start_time": "2024-01-15T10:00:00",
    "duration_minutes": 60,
    "location": "Salle de conférence",
    "priority": "high",
    "is_flexible": false,
    "category_id": 1
  }'
```

### Planifier automatiquement un événement

```bash
curl -X POST "http://localhost:8000/events/schedule" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Formation",
    "description": "Formation sur les nouvelles technologies",
    "start_time": "2024-01-15T14:00:00",
    "duration_minutes": 120,
    "priority": "medium",
    "is_flexible": true,
    "category_id": 1
  }'
```

### Récupérer le planning quotidien

```bash
curl "http://localhost:8000/schedule/daily?date=2024-01-15T00:00:00"
```

## 🧪 Tests

```bash
# Lancer tous les tests
uv run pytest

# Lancer les tests avec couverture
uv run pytest --cov=src

# Lancer les tests en mode verbose
uv run pytest -v
```

## 🏗️ Architecture

### Structure du projet

```
kairos-backend/
├── src/
│   └── kairos_backend/
│       ├── __init__.py
│       ├── api.py          # API FastAPI
│       ├── models.py       # Modèles SQLAlchemy et Pydantic
│       ├── database.py     # Configuration base de données
│       └── scheduler.py    # Logique de scheduling
├── tests/
│   ├── __init__.py
│   └── test_api.py        # Tests de l'API
├── main.py                # Point d'entrée
├── pyproject.toml         # Configuration du projet
└── README.md
```

### Modèles de données

#### Event (Événement)
- `id` : Identifiant unique
- `title` : Titre de l'événement
- `description` : Description optionnelle
- `start_time` : Heure de début
- `end_time` : Heure de fin (calculée automatiquement)
- `location` : Lieu optionnel
- `priority` : Priorité (high/medium/low)
- `is_flexible` : Peut être déplacé automatiquement
- `category_id` : Référence vers la catégorie

#### Category (Catégorie)
- `id` : Identifiant unique
- `name` : Nom de la catégorie
- `color_code` : Code couleur hexadécimal
- `description` : Description optionnelle

## 🤖 Intelligence du Scheduling

### Algorithme de placement

1. **Vérification du créneau préféré** : Test de disponibilité
2. **Détection de conflits** : Identification des chevauchements
3. **Résolution intelligente** : 
   - Pour les événements haute priorité : proposition de déplacement des événements flexibles
   - Recherche de créneaux alternatifs dans les heures de travail (8h-20h)
4. **Optimisation** : Placement par créneaux de 30 minutes

### Gestion des conflits

- **Événements flexibles** : Peuvent être déplacés automatiquement
- **Priorités** : Les événements haute priorité peuvent déplacer les autres
- **Suggestions** : Propositions de résolution avec justification

## 🔧 Configuration

### Variables d'environnement

- `DATABASE_URL` : URL de la base de données (défaut: `sqlite:///./kairos.db`)

### Catégories par défaut

Le système initialise automatiquement 4 catégories :
- **Travail** (#3B82F6) - Événements professionnels
- **Perso** (#10B981) - Événements personnels  
- **Sport** (#F59E0B) - Activités sportives
- **Repos** (#8B5CF6) - Temps de repos et détente

## 🚧 Développement futur

### Fonctionnalités prévues

- [ ] Récurrence d'événements
- [ ] Notifications et rappels
- [ ] Synchronisation avec calendriers externes
- [ ] Gestion des invités et participants
- [ ] Statistiques et rapports
- [ ] Interface web frontend
- [ ] Application mobile

### Améliorations techniques

- [ ] Authentification et autorisation
- [ ] Cache Redis pour les performances
- [ ] Base de données PostgreSQL pour la production
- [ ] Déploiement Docker
- [ ] CI/CD avec GitHub Actions

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Forker le projet
2. Créer une branche feature
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request
