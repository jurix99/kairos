"""
Routes API pour Kairos Backend
"""

from .categories import router as categories_router
from .events import router as events_router
from .scheduling import router as scheduling_router
from .auth import router as auth_router
from .assistant import router as assistant_router
from .goals import router as goals_router
from .suggestions import router as suggestions_router
from .orchestration import router as orchestration_router

__all__ = ["categories_router", "events_router", "scheduling_router", "auth_router", "assistant_router", "goals_router", "suggestions_router", "orchestration_router"] 