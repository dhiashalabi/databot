"""Application configuration using environment management."""

from .env import env


class Settings:
	"""Application settings using centralized environment configuration."""

	DB_USER: str = env.DB_USER
	DB_PASSWORD: str = env.DB_PASSWORD
	DB_HOST: str = env.DB_HOST
	DB_PORT: str = env.DB_PORT
	DB_NAME: str = env.DB_NAME

	APP_NAME: str = env.APP_NAME
	APP_VERSION: str = env.APP_VERSION
	DEBUG: bool = env.DEBUG
	LOG_LEVEL: str = env.LOG_LEVEL

	OPENAI_API_KEY: str = env.OPENAI_API_KEY
	OPENAI_MODEL: str = env.OPENAI_MODEL

	@property
	def database_url(self) -> str:
		"""Generate database URL for async connections."""
		return env.get_database_url()

	@property
	def asyncpg_url(self) -> str:
		"""Generate asyncpg connection URL."""
		return env.get_asyncpg_url()


settings = Settings()
