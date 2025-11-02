"""
Configuration pour Kairos Backend
"""

from .database import get_db, create_tables, init_default_categories
from .settings import settings

__all__ = ["get_db", "create_tables", "init_default_categories", "settings"] 