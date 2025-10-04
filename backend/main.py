"""Main FastAPI application."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api import api_router
from src.config import settings
from src.database import close_db, init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""Application lifespan events."""
	await init_db()
	yield
	await close_db()


app = FastAPI(
	title=settings.APP_NAME,
	version=settings.APP_VERSION,
	lifespan=lifespan,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000", "http://localhost:3001"],
	allow_credentials=True,
	allow_methods=["POST", "GET", "OPTIONS"],
	allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)


@app.get("/")
async def read_root():
	"""Root endpoint."""
	return {
		"message": "Welcome to DataBot API",
		"version": settings.APP_VERSION,
		"docs": "/docs",
	}
