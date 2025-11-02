# 🐳 Docker Setup pour Kairos Refactor

## Configuration

### 1. Variables d'environnement

Créez un fichier `.env` à la **racine du projet** (pas dans refactor/) :

```env
# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
```

### 2. Lancer avec Docker Compose

Depuis la **racine du projet** :

```bash
# Build et démarrer tous les services
docker-compose up --build

# Ou en arrière-plan
docker-compose up -d --build
```

### 3. Accéder à l'application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **PostgreSQL:** localhost:5432

### 4. Arrêter les services

```bash
# Arrêter
docker-compose down

# Arrêter et supprimer les volumes (données)
docker-compose down -v
```

## Services

Le `docker-compose.yml` lance 3 services :

1. **postgres** - Base de données PostgreSQL
2. **backend** - API FastAPI
3. **frontend** - Application Next.js (refactor)

## Développement

### Logs en temps réel

```bash
# Tous les services
docker-compose logs -f

# Juste le frontend
docker-compose logs -f frontend

# Juste le backend
docker-compose logs -f backend
```

### Rebuild un service spécifique

```bash
# Rebuild juste le frontend
docker-compose up -d --build frontend
```

### Entrer dans un conteneur

```bash
# Frontend
docker exec -it kairos-frontend sh

# Backend
docker exec -it kairos-backend sh

# PostgreSQL
docker exec -it kairos-postgres psql -U kairos_user -d kairos
```

## Troubleshooting

### Erreur : "Port 3000 already in use"

Arrêtez le serveur Next.js local avant de lancer Docker :

```bash
# Tuer le processus sur le port 3000
# Windows PowerShell:
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -Force

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Problème de build

Supprimez les images et volumes puis rebuild :

```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Le frontend ne se connecte pas au backend

Vérifiez que `NEXT_PUBLIC_API_URL` pointe bien vers `http://localhost:8000` dans le docker-compose.yml.

## Production

Pour un déploiement en production, modifiez le Dockerfile :

1. Décommentez la ligne `RUN npm run build` dans le Dockerfile
2. Changez la commande finale de `npm run dev` à `npm start`
3. Changez `NODE_ENV` de `development` à `production`

```dockerfile
ENV NODE_ENV production
CMD ["npm", "start"]
```

Puis rebuild :

```bash
docker-compose up -d --build
```

