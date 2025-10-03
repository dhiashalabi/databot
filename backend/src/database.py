"""Database configuration and session management."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(
	settings.database_url,
	echo=settings.DEBUG,
	future=True,
)

async_session_maker = async_sessionmaker(
	engine,
	class_=AsyncSession,
	expire_on_commit=False,
)


class Base(DeclarativeBase):
	"""Base class for all database models."""

	pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	"""Dependency for getting async database sessions.

	Yields:
		AsyncSession: Database session.

	"""
	async with async_session_maker() as session:
		try:
			yield session
		finally:
			await session.close()


async def close_db() -> None:
	"""Close database connections."""
	await engine.dispose()
