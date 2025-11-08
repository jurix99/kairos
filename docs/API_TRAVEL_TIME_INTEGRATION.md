# Guide d'Intégration API pour les Temps de Trajet

## 📋 Vue d'ensemble

Le système de scheduling intelligent supporte maintenant le calcul automatique des temps de trajet via des APIs de cartographie externes. Cette fonctionnalité permet d'obtenir des estimations précises basées sur les données réelles de trafic et de distance.

## 🔧 Configuration

### 1. Google Maps Distance Matrix API

**Obtenir une clé API :**
1. Créer un compte sur [Google Cloud Console](https://console.cloud.google.com/)
2. Activer l'API "Distance Matrix API"
3. Créer une clé API avec les restrictions appropriées

**Configuration dans `.env` :**
```env
TRAVEL_API_PROVIDER=google
TRAVEL_API_KEY=AIzaSy...votre_cle_api
USE_TRAVEL_API=true
```

### 2. Mapbox Directions API (à venir)

**Configuration dans `.env` :**
```env
TRAVEL_API_PROVIDER=mapbox
TRAVEL_API_KEY=pk.ey...votre_cle_api
USE_TRAVEL_API=true
```

### 3. OpenRouteService API (à venir)

**Configuration dans `.env` :**
```env
TRAVEL_API_PROVIDER=openroute
TRAVEL_API_KEY=5b3c...votre_cle_api
USE_TRAVEL_API=true
```

## 🚀 Utilisation

### Mode Global

Quand `USE_TRAVEL_API=true` est configuré, toutes les requêtes utilisent l'API par défaut :

```python
from backend.services.travel_service import TravelService
from backend.config.settings import settings

# Service avec configuration globale
service = TravelService(
    api_provider=settings.TRAVEL_API_PROVIDER,
    api_key=settings.TRAVEL_API_KEY,
    use_api=settings.USE_TRAVEL_API
)

# Utilise l'API si configurée
travel_time = service.calculate_travel_time(
    "Tour Eiffel, Paris",
    "Arc de Triomphe, Paris"
)
```

### Mode Par Requête

Vous pouvez forcer l'utilisation de l'API ou des heuristiques pour chaque calcul :

```python
# Forcer l'utilisation de l'API
travel_time = service.calculate_travel_time(
    origin="Paris",
    destination="Lyon",
    use_api=True
)

# Forcer l'utilisation des heuristiques
travel_time = service.calculate_travel_time(
    origin="Paris",
    destination="Lyon",
    use_api=False
)
```

### Via l'API REST

**Calcul avec API :**
```bash
curl -X POST "http://localhost:8080/smart-schedule/calculate-travel-time?use_api=true" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Tour Eiffel, 75007 Paris",
    "destination": "Musée du Louvre, 75001 Paris"
  }'
```

**Réponse :**
```json
{
  "origin": "Tour Eiffel, 75007 Paris",
  "destination": "Musée du Louvre, 75001 Paris",
  "travel_time_minutes": 12,
  "travel_time": "0:12:00",
  "needs_buffer": true,
  "method": "api",
  "warning_message": "Votre trajet entre 'Tour Eiffel, 75007 Paris' et 'Musée du Louvre, 75001 Paris' prend environ 12 min"
}
```

**Calcul avec heuristiques :**
```bash
curl -X POST "http://localhost:8080/smart-schedule/calculate-travel-time?use_api=false" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Paris",
    "destination": "Lyon"
  }'
```

**Réponse :**
```json
{
  "origin": "Paris",
  "destination": "Lyon",
  "travel_time_minutes": 60,
  "travel_time": "1:00:00",
  "needs_buffer": true,
  "method": "heuristic",
  "warning_message": "Votre trajet entre 'Paris' et 'Lyon' prend environ 60 min"
}
```

## 🔄 Stratégie de Fallback

Le système implémente un fallback automatique :

1. **Tentative API** : Si `use_api=true` et configuration valide
2. **Fallback heuristique** : Si l'API échoue ou n'est pas configurée
3. **Cache** : Résultats mis en cache pour éviter les appels répétés

```python
# Exemple de comportement
service = TravelService(
    api_provider="google",
    api_key="invalid_key",
    use_api=True
)

# Essaie l'API, échoue, utilise les heuristiques
# → Aucune erreur lancée, calcul transparent
travel_time = service.calculate_travel_time("Paris", "Lyon")
```

## 💰 Coûts et Limites

### Google Maps Distance Matrix API

**Gratuit :**
- $200 de crédit mensuel gratuit
- ~40,000 requêtes gratuites/mois

**Tarifs :**
- $5 par 1000 requêtes au-delà du crédit gratuit

**Limites :**
- 100 éléments par requête
- 100 requêtes par seconde

### Recommandations

1. **Utiliser le cache** : Activé par défaut
2. **Mode hybride** : API pour les calculs critiques, heuristiques pour les estimations
3. **Monitoring** : Surveiller l'utilisation via Google Cloud Console

## 🧪 Tests

### Tester l'Intégration

```bash
cd backend

# Tests avec mock API
pytest tests/test_travel_service.py::TestTravelService::test_api_integration_initialization -v

# Test du fallback
pytest tests/test_travel_service.py::TestTravelService::test_api_fallback_to_heuristic -v
```

### Tester Manuellement

```python
from backend.services.travel_service import TravelService

# Test avec vraie API Google Maps
service = TravelService(
    api_provider="google",
    api_key="VOTRE_CLE_API",
    use_api=True
)

# Calcul réel
result = service.get_travel_info(
    "Eiffel Tower, Paris, France",
    "Louvre Museum, Paris, France",
    use_api=True
)

print(f"Méthode: {result['method']}")
print(f"Temps: {result['travel_time_minutes']} minutes")
```

## 🔒 Sécurité

### Bonnes Pratiques

1. **Ne jamais committer les clés API** dans le code
2. **Utiliser les variables d'environnement** `.env`
3. **Restreindre les clés API** dans la console du fournisseur :
   - Par domaine (production)
   - Par IP (développement)
   - Par API (activer uniquement Distance Matrix)

### Configuration de Production

```env
# Production
TRAVEL_API_PROVIDER=google
TRAVEL_API_KEY=${GOOGLE_MAPS_API_KEY}  # Variable d'environnement sécurisée
USE_TRAVEL_API=true

# Rate limiting recommandé
TRAVEL_API_RATE_LIMIT=100  # requêtes/minute
```

## 📊 Monitoring

### Logs

Le service log automatiquement :
- Succès/échecs des appels API
- Fallback sur heuristiques
- Erreurs de configuration

```python
import logging

logger = logging.getLogger("backend.services.travel_service")
logger.setLevel(logging.INFO)

# Les logs incluent :
# - "API returned no result, falling back to heuristics"
# - "Error calculating travel time via API: ..., falling back to heuristics"
```

### Métriques Recommandées

1. **Taux de succès API** : Ratio succès/échecs
2. **Temps de réponse** : Latence moyenne
3. **Utilisation du cache** : Hit rate
4. **Coût mensuel** : Via Google Cloud Console

## 🚀 Migration

### Passer des Heuristiques à l'API

**Étape 1 : Configurer l'API**
```bash
# Ajouter dans .env
TRAVEL_API_PROVIDER=google
TRAVEL_API_KEY=votre_cle_api
USE_TRAVEL_API=false  # Laisser false initialement
```

**Étape 2 : Tester**
```bash
# Tester avec des requêtes ponctuelles
curl -X POST "http://localhost:8080/smart-schedule/calculate-travel-time?use_api=true" ...
```

**Étape 3 : Activer Globalement**
```bash
# Une fois validé
USE_TRAVEL_API=true
```

### Retour aux Heuristiques

Simple changement de configuration :
```bash
USE_TRAVEL_API=false
```

## 📖 Documentation Complète

- **Documentation principale** : [SMART_SCHEDULING.md](./SMART_SCHEDULING.md)
- **Configuration** : [env.example](../env.example)
- **Tests** : [test_travel_service.py](../backend/tests/test_travel_service.py)

## 🆘 Dépannage

### Problème : API retourne des erreurs

**Solution :**
1. Vérifier la validité de la clé API
2. Vérifier que l'API Distance Matrix est activée
3. Vérifier les restrictions de la clé (domaine, IP)
4. Vérifier les quotas/limites

### Problème : Calculs incohérents

**Solution :**
1. Vider le cache : `TravelService.clear_cache()`
2. Vérifier le format des adresses (précision)
3. Comparer API vs heuristique

### Problème : Coûts élevés

**Solution :**
1. Activer le mode hybride (API sur demande uniquement)
2. Augmenter la durée de cache
3. Utiliser l'API uniquement pour les calculs critiques

---

**Fait avec ❤️ pour Kairos**
