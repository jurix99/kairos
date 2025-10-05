# Kairos Refactor - Modern Frontend

Ce dossier contient le nouveau frontend Kairos construit avec Next.js 14+ et shadcn/ui.

## Configuration requise

### Variables d'environnement

Créez un fichier `.env.local` à la racine du dossier `refactor` avec les variables suivantes :

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# GitHub OAuth Configuration
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id_here
NEXT_PUBLIC_GITHUB_REDIRECT_URI=http://localhost:3000
```

## Installation

```bash
npm install
```

## Développement

```bash
npm run dev
```

## Fonctionnalités intégrées

✅ **Authentification**
- Login avec GitHub OAuth
- Gestion de session avec localStorage
- Protection des routes

✅ **Dashboard**
- Affichage des statistiques d'événements
- Cartes KPI (Total Events, Completed, In Progress, High Priority)
- Charts interactifs
- Chargement des données depuis l'API backend

✅ **API Integration**
- Client API pour communiquer avec le backend FastAPI
- Gestion des événements (CRUD)
- Gestion des catégories
- Gestion des erreurs

## Structure

```
refactor/
├── app/
│   ├── dashboard/
│   │   └── page.tsx          # Page principale du dashboard
│   ├── login/
│   │   └── page.tsx          # Page de connexion
│   └── layout.tsx            # Layout root avec AuthProvider
├── components/
│   ├── app-sidebar.tsx       # Sidebar principale
│   ├── login-form.tsx        # Formulaire de connexion
│   ├── section-cards.tsx     # Cartes de statistiques
│   └── ...
├── contexts/
│   └── auth-context.tsx      # Contexte d'authentification
└── lib/
    └── api.ts                # Client API
```

## Points d'intégration avec le backend

Le frontend communique avec le backend via les endpoints suivants :

- `POST /auth/github/callback` - Authentification GitHub
- `GET /events` - Récupération de tous les événements
- `POST /events` - Création d'un événement
- `PUT /events/:id` - Modification d'un événement
- `DELETE /events/:id` - Suppression d'un événement
- `GET /categories` - Récupération des catégories
- `POST /categories` - Création d'une catégorie

## TODO

- [ ] Adapter ChartAreaInteractive pour afficher les données d'événements
- [ ] Créer une vue Calendar
- [ ] Ajouter la gestion des événements (création, édition, suppression)
- [ ] Améliorer la gestion des erreurs
- [ ] Ajouter des tests

