FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de configuration Python et le README
COPY pyproject.toml ./
COPY uv.lock ./

# Installer uv pour la gestion des dépendances
RUN pip install uv

# Installer les dépendances Python
RUN uv sync --frozen

# Copier le code source
COPY . .

# Exposer le port
EXPOSE 8000

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://kairos_user:kairos_password@postgres:5432/kairos

# Commande par défaut
CMD ["uv", "run", "uvicorn", "src.kairos_backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
