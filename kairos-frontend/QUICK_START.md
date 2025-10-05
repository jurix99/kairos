# 🚀 Guide de Démarrage Rapide - Kairos Refactor

## ✅ Ce qui a été fait

### 1. **Authentification complète**
- ✅ Login avec GitHub OAuth
- ✅ Gestion de session persistante (localStorage)
- ✅ Protection des routes (redirect vers /login si non authentifié)
- ✅ Callback GitHub avec gestion d'erreurs
- ✅ Fallback utilisateur test pour le développement

### 2. **Dashboard intégré avec l'API**
- ✅ Récupération automatique des événements depuis l'API
- ✅ Récupération des catégories
- ✅ Affichage des statistiques en temps réel :
  - Total d'événements
  - Événements complétés (avec taux de complétion)
  - Événements en cours
  - Événements haute priorité
- ✅ Gestion des erreurs de connexion backend
- ✅ États de chargement

### 3. **API Client**
- ✅ Client complet pour communiquer avec le backend FastAPI
- ✅ Endpoints implémentés :
  - Authentification GitHub
  - CRUD événements
  - Récupération catégories
- ✅ Types TypeScript pour toutes les entités

### 4. **UI/UX Moderne**
- ✅ Interface sombre (dark mode) par défaut
- ✅ Sidebar collapsible avec shadcn/ui
- ✅ Cartes KPI avec icônes et badges
- ✅ Design responsive
- ✅ Animations de chargement

## 📋 Pour démarrer

### 1. Installation des dépendances

```bash
cd refactor
npm install
```

**Note :** Tous les fichiers de configuration sont déjà créés (`package.json`, `tsconfig.json`, `tailwind.config.ts`, etc.)

### 2. Configuration des variables d'environnement

Créez un fichier `.env.local` dans le dossier `refactor` :

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# GitHub OAuth (utilisez les mêmes que votre ancien frontend)
NEXT_PUBLIC_GITHUB_CLIENT_ID=votre_client_id
NEXT_PUBLIC_GITHUB_REDIRECT_URI=http://localhost:3000
```

### 3. Démarrage

**Terminal 1 - Backend :**
```bash
cd kairos-backend
python main.py
```

**Terminal 2 - Frontend :**
```bash
cd refactor
npm run dev
```

### 4. Accès

- Frontend : `http://localhost:3000` (redirige automatiquement vers /login ou /dashboard)
- Backend API : `http://localhost:8000`

## 🎯 Workflow d'utilisation

1. **Login** : Cliquez sur "Login with GitHub" sur `/login`
2. **Callback** : Après authentification GitHub, redirection automatique vers `/dashboard`
3. **Dashboard** : Visualisation des statistiques de vos événements
4. **Navigation** : Utilisez la sidebar pour naviguer (Dashboard, Calendar, Analytics, Settings)

## 🔧 Prochaines étapes suggérées

### Priorité Haute
- [ ] Adapter `ChartAreaInteractive` pour afficher les événements sur un timeline
- [ ] Créer la page Calendar (`/calendar`)
- [ ] Ajouter des formulaires pour créer/éditer des événements

### Priorité Moyenne
- [ ] Page Analytics détaillée
- [ ] Filtrage des événements par catégorie
- [ ] Recherche d'événements
- [ ] Export des données

### Priorité Basse
- [ ] Page Settings pour gérer le profil
- [ ] Thème clair/sombre toggle
- [ ] Notifications
- [ ] Multi-langue

## 🐛 Troubleshooting

### Erreur : "Failed to load data"
- ✅ Vérifiez que le backend est bien démarré sur `http://localhost:8000`
- ✅ Vérifiez que `NEXT_PUBLIC_API_URL` est correct dans `.env.local`
- ✅ Vérifiez les CORS dans le backend

### Erreur : "GitHub auth failed"
- ✅ Vérifiez `NEXT_PUBLIC_GITHUB_CLIENT_ID` dans `.env.local`
- ✅ Vérifiez que le redirect URI est bien configuré dans GitHub OAuth Apps
- ✅ Le backend doit avoir les variables d'environnement GitHub configurées

### Pas de données affichées
- ✅ Créez quelques événements via l'ancien frontend ou directement via l'API
- ✅ Vérifiez que l'utilisateur est bien authentifié
- ✅ Ouvrez la console du navigateur pour voir les erreurs éventuelles

## 📁 Structure des fichiers clés

```
refactor/
├── app/
│   ├── layout.tsx              # Layout root avec AuthProvider
│   ├── login/
│   │   └── page.tsx            # Page de login + callback GitHub
│   └── dashboard/
│       └── page.tsx            # Dashboard principal
├── components/
│   ├── app-sidebar.tsx         # Sidebar adaptée pour Kairos
│   ├── login-form.tsx          # Formulaire de connexion
│   ├── section-cards.tsx       # Cartes KPI avec stats événements
│   └── site-header.tsx         # Header avec nom utilisateur
├── contexts/
│   └── auth-context.tsx        # Gestion globale de l'auth
├── lib/
│   └── api.ts                  # Client API TypeScript
└── .env.local                  # Variables d'environnement (à créer)
```

## 🎨 Personnalisation

Les couleurs principales de Kairos sont définies dans le thème :
- Primaire : Purple-600 (#9333ea)
- Secondaire : Pink-600 (#db2777)
- Background : Dark mode par défaut

Pour modifier, éditez `app/globals.css` et les composants UI dans `components/ui/`.

## 💡 Tips

1. **Mode développement** : Si le backend n'est pas disponible, un utilisateur test est automatiquement créé
2. **Données de test** : Utilisez l'ancien frontend pour créer des événements si vous démarrez de zéro
3. **Hot reload** : Next.js recharge automatiquement lors des modifications
4. **Types** : Tous les types API sont dans `lib/api.ts` - modifiez-les si le backend change

## 📞 Support

Si vous rencontrez des problèmes, vérifiez :
1. Les logs du backend FastAPI
2. La console du navigateur
3. Les network requests dans l'onglet Network des DevTools

