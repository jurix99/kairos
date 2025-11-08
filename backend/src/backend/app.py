"""
Application FastAPI principale pour Kairos Backend
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.database import create_tables, init_default_categories, get_db
from .config.settings import settings
from .routes import categories_router, events_router, scheduling_router, auth_router, assistant_router, goals_router, suggestions_router, orchestration_router

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À configurer selon vos besoins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(categories_router)
app.include_router(events_router)
app.include_router(scheduling_router)
app.include_router(auth_router)
app.include_router(assistant_router)
app.include_router(goals_router)
app.include_router(suggestions_router)
app.include_router(orchestration_router)


@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    logger.info("Démarrage de l'application Kairos")
    logger.info(f"Mode debug: {settings.DEBUG}")
    logger.info(f"URL de la base de données: {settings.DATABASE_URL}")
    logger.info(f"Clé OpenAI configurée: {'Oui' if settings.OPENAI_API_KEY else 'Non'}")
    
    create_tables()
    # Initialiser les catégories par défaut
    db = next(get_db())
    init_default_categories(db)
    
    logger.info("Application démarrée avec succès")


@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "Bienvenue sur Kairos Backend - Agenda Intelligent",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy", 
        "message": "Kairos Backend is running",
        "version": settings.API_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    ) 