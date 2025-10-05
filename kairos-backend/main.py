"""
Point d'entrée principal pour Kairos Backend
"""

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.kairos_backend.app:app",  # Utiliser une chaîne d'import
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
