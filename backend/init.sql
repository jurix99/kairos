-- Script d'initialisation pour la base de données PostgreSQL Kairos
-- Ce script est exécuté automatiquement lors du premier démarrage du conteneur PostgreSQL

-- Créer des extensions utiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Créer un utilisateur pour l'application (optionnel, car déjà créé par les variables d'environnement)
-- CREATE USER kairos_user WITH ENCRYPTED PASSWORD 'kairos_password';
-- GRANT ALL PRIVILEGES ON DATABASE kairos TO kairos_user;

-- Message de confirmation
SELECT 'Base de données Kairos initialisée avec succès!' as message; 