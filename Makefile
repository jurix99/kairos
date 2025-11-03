# Makefile pour Kairos - Agenda Intelligent
# Utilisation: make <commande>

.PHONY: help setup build up down restart logs clean status shell-backend shell-frontend shell-db backup restore

# Couleurs pour l'affichage
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

# Commande par défaut
help: ## Afficher l'aide
	@echo "$(GREEN)🚀 Kairos - Commandes disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## Configuration initiale (copie env.example vers .env)
	@echo "$(GREEN)📋 Configuration initiale...$(NC)"
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "$(YELLOW)⚠️  Fichier .env créé. Veuillez le configurer avec vos paramètres.$(NC)"; \
		echo "$(YELLOW)   Notamment GITHUB_CLIENT_SECRET pour l'authentification OAuth.$(NC)"; \
	else \
		echo "$(GREEN)✅ Fichier .env déjà présent.$(NC)"; \
	fi

build: ## Construire toutes les images Docker
	@echo "$(GREEN)🏗️  Construction des images Docker...$(NC)"
	docker-compose build

up: setup ## Démarrer tous les services
	@echo "$(GREEN)🚀 Démarrage des services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Services démarrés !$(NC)"
	@echo "$(YELLOW)🌐 Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)🔧 Backend: http://localhost:8080$(NC)"
	@echo "$(YELLOW)📚 API Docs: http://localhost:8080/docs$(NC)"

down: ## Arrêter tous les services
	@echo "$(GREEN)🛑 Arrêt des services...$(NC)"
	docker-compose down

restart: ## Redémarrer tous les services
	@echo "$(GREEN)🔄 Redémarrage des services...$(NC)"
	docker-compose restart

restart-backend: ## Redémarrer le backend uniquement
	@echo "$(GREEN)🔄 Redémarrage du backend...$(NC)"
	docker-compose restart backend

restart-frontend: ## Redémarrer le frontend uniquement
	@echo "$(GREEN)🔄 Redémarrage du frontend...$(NC)"
	docker-compose restart frontend

logs: ## Voir tous les logs
	docker-compose logs -f

logs-backend: ## Voir les logs du backend
	docker-compose logs -f backend

logs-frontend: ## Voir les logs du frontend
	docker-compose logs -f frontend

logs-db: ## Voir les logs de la base de données
	docker-compose logs -f postgres

status: ## Voir l'état des services
	@echo "$(GREEN)📊 État des services:$(NC)"
	docker-compose ps

shell-backend: ## Accéder au shell du backend
	docker-compose exec backend bash

shell-frontend: ## Accéder au shell du frontend
	docker-compose exec frontend sh

shell-db: ## Accéder au shell PostgreSQL
	docker-compose exec postgres psql -U kairos_user -d kairos

clean: ## Nettoyer (arrêter et supprimer les conteneurs)
	@echo "$(RED)🧹 Nettoyage des conteneurs...$(NC)"
	docker-compose down
	docker-compose rm -f

clean-all: ## Nettoyage complet (conteneurs + volumes + images)
	@echo "$(RED)⚠️  Nettoyage complet (perte de données)...$(NC)"
	docker-compose down -v
	docker-compose rm -f
	docker rmi kairos-backend kairos-frontend 2>/dev/null || true

backup: ## Sauvegarder la base de données
	@echo "$(GREEN)💾 Sauvegarde de la base de données...$(NC)"
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U kairos_user kairos > backups/kairos_backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Sauvegarde terminée dans le dossier backups/$(NC)"

restore: ## Restaurer la base de données (usage: make restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)❌ Veuillez spécifier le fichier: make restore FILE=backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🔄 Restauration de la base de données...$(NC)"
	docker-compose exec -T postgres psql -U kairos_user kairos < $(FILE)
	@echo "$(GREEN)✅ Restauration terminée$(NC)"

dev: ## Mode développement (avec rebuild automatique)
	@echo "$(GREEN)🔧 Mode développement...$(NC)"
	docker-compose up --build

prod-build: ## Construction pour la production
	@echo "$(GREEN)🏭 Construction pour la production...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

test-backend: ## Exécuter les tests du backend
	docker-compose exec backend python -m pytest

install-backend: ## Installer les dépendances du backend
	docker-compose exec backend uv sync

install-frontend: ## Installer les dépendances du frontend
	docker-compose exec frontend npm install

migrate: ## Exécuter les migrations de base de données
	docker-compose exec backend python migrate.py 