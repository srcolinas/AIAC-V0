"""API routes package."""
from app.api.auth import router as auth_router
from app.api.games import router as games_router
from app.api.websocket import router as ws_router

__all__ = ["auth_router", "games_router", "ws_router"]

