"""
Routes API pour Kairos Backend
"""

from .categories import router as categories_router
from .events import router as events_router
from .scheduling import router as scheduling_router
from .auth import router as auth_router

__all__ = ["categories_router", "events_router", "scheduling_router", "auth_router"] 