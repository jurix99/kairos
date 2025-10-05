# Dockerfile pour Kairos Frontend (Next.js) - Mode Développement
FROM node:20-alpine

# Installation des dépendances système
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Variables d'environnement
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1

# Copie des fichiers de dépendances
COPY package.json package-lock.json ./

# Nettoie le cache npm et installe les dépendances
RUN npm cache clean --force && \
    npm install --legacy-peer-deps

# Copie de tous les fichiers du projet
COPY . .

# Le dossier .next sera créé au premier lancement
# Les volumes monteront le code source pour le hot-reload

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Lancer le serveur de développement
CMD ["npm", "run", "dev"]

