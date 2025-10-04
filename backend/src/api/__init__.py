"""API routers."""

from fastapi import APIRouter

from src.api import auth, chat, health, models

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(models.router, tags=["models"])

__all__ = ["api_router"]
