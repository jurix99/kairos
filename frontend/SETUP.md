# 🚀 Setup Kairos Refactor

## Étapes rapides

### 1️⃣ Installer les dépendances

```bash
cd refactor
npm install
```

### 2️⃣ Créer le fichier `.env.local`

Créez un fichier `.env.local` dans le dossier `refactor` avec :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GITHUB_CLIENT_ID=votre_github_client_id
NEXT_PUBLIC_GITHUB_REDIRECT_URI=http://localhost:3000
```

> **Note :** Récupérez vos credentials GitHub depuis : https://github.com/settings/developers

### 3️⃣ Démarrer le backend

```bash
cd ../backend
python main.py
```

### 4️⃣ Démarrer le frontend

Dans un nouveau terminal :

```bash
cd refactor
npm run dev
```

### 5️⃣ Ouvrir l'application

Allez sur : **http://localhost:3000**

## ✅ Fichiers créés

Tous les fichiers de configuration nécessaires ont été créés :

- ✅ `package.json` - Dépendances du projet
- ✅ `tsconfig.json` - Configuration TypeScript
- ✅ `tailwind.config.ts` - Configuration Tailwind CSS
- ✅ `postcss.config.mjs` - Configuration PostCSS
- ✅ `next.config.mjs` - Configuration Next.js
- ✅ `app/globals.css` - Styles globaux avec thème dark
- ✅ `lib/utils.ts` - Utilitaires
- ✅ `hooks/use-mobile.tsx` - Hook pour détection mobile
- ✅ `app/page.tsx` - Page d'accueil (redirection)
- ✅ `.gitignore` - Fichiers à ignorer
- ✅ `.eslintrc.json` - Configuration ESLint

## 🎨 Thème

Le thème est configuré en **dark mode par défaut** avec les couleurs Kairos :
- Primaire : Purple (#9333ea)
- Secondaire : Pink (#db2777)
- Background : `#0a0a0a`
- Cards : `#171717`

## 📚 Documentation complète

Pour plus de détails, consultez :
- `QUICK_START.md` - Guide détaillé avec troubleshooting
- `README.md` - Vue d'ensemble du projet

## 🆘 Problèmes courants

### Erreur : "Cannot find module"
```bash
rm -rf node_modules package-lock.json
npm install
```

### Backend non disponible
Le frontend fonctionne quand même avec un utilisateur de test en fallback.

### Port 3000 déjà utilisé
```bash
npm run dev -- -p 3001
```

---

**Vous êtes prêt ! 🎉**

