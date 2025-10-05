"""API routers."""

from fastapi import APIRouter

from src.api import ai_feedback, auth, chat, health, models, tokens, users

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(models.router, tags=["models"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(tokens.router, prefix="/tokens", tags=["tokens"])
api_router.include_router(ai_feedback.router, prefix="/ai", tags=["ai_feedback"])

__all__ = ["api_router"]
