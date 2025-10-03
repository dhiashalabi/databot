"""Application configuration."""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
	"""Application settings."""

	# Database configuration
	DB_USER: str = os.getenv("DB_USER", "postgres")
	DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
	DB_HOST: str = os.getenv("DB_HOST", "localhost")
	DB_PORT: str = os.getenv("DB_PORT", "5432")
	DB_NAME: str = os.getenv("DB_NAME", "databot")

	# Application configuration
	APP_NAME: str = "DataBot API"
	APP_VERSION: str = "0.1.0"
	DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

	# OpenAI configuration
	OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
	OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

	@property
	def database_url(self) -> str:
		"""Generate database URL for async connections."""
		return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
	
	@property
	def asyncpg_url(self) -> str:
		"""Generate asyncpg connection URL."""
		return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
