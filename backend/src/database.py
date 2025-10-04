"""Database configuration and session management."""

import asyncio
from collections.abc import AsyncGenerator
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

logger = logging.getLogger(__name__)

engine: object | None = None
async_session_maker: object | None = None
_initialization_lock = asyncio.Lock()
_is_initialized = False


async def init_db() -> None:
	"""Initialize database engine and session maker."""
	global engine, async_session_maker, _is_initialized

	async with _initialization_lock:
		if _is_initialized:
			return

		try:
			engine = create_async_engine(
				settings.database_url,
				echo=settings.DEBUG,
				future=True,
				pool_pre_ping=True,
				pool_recycle=3600,
			)

			async_session_maker = async_sessionmaker(
				engine,
				class_=AsyncSession,
				expire_on_commit=False,
			)

			async with async_session_maker() as session:
				await session.execute(text("SELECT 1"))

			_is_initialized = True

		except Exception as e:
			logger.error(f"Database initialization failed: {e}")
			raise


async def get_session_maker():
	"""Get the session maker, initializing if needed."""
	if not _is_initialized:
		await init_db()
	return async_session_maker


async def get_engine():
	"""Get the database engine, initializing if needed."""
	if not _is_initialized:
		await init_db()
	return engine


class Base(DeclarativeBase):
	"""Base class for all database models."""

	pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	"""Dependency for getting async database sessions.

	Yields:
		AsyncSession: Database session.
	"""
	if not _is_initialized:
		await init_db()

	async with async_session_maker() as session:
		try:
			yield session
		finally:
			await session.close()


async def close_db() -> None:
	"""Close database connections."""
	global _is_initialized

	if engine:
		await engine.dispose()
		_is_initialized = False


async def health_check() -> dict:
	"""Check database health."""
	try:
		if not _is_initialized:
			await init_db()

		async with async_session_maker() as session:
			await session.execute(text("SELECT 1"))

		return {"status": "healthy", "message": "Database connection is working"}
	except Exception as e:
		logger.error(f"Database health check failed: {e}")
		return {"status": "unhealthy", "message": f"Database error: {str(e)}"}
