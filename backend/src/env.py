"""Environment variable management and validation."""

import logging
import os
from typing import Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class EnvConfig:
	"""Centralized environment variable configuration."""

	DB_USER: str = os.getenv("DB_USER", "postgres")
	DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
	DB_HOST: str = os.getenv("DB_HOST", "localhost")
	DB_PORT: str = os.getenv("DB_PORT", "5432")
	DB_NAME: str = os.getenv("DB_NAME", "databot")

	APP_NAME: str = os.getenv("APP_NAME", "DataBot API")
	APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
	DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
	LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

	OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
	OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

	MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "databot-mcp-server")
	MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
	MCP_MAX_TOOLS_PER_REQUEST: int = int(os.getenv("MCP_MAX_TOOLS_PER_REQUEST", "50"))
	MCP_DEFAULT_TOOL_TIMEOUT: int = int(os.getenv("MCP_DEFAULT_TOOL_TIMEOUT", "30"))
	MCP_LOG_LEVEL: str = os.getenv("MCP_LOG_LEVEL", "INFO")
	MCP_LOG_FORMAT: str = os.getenv(
		"MCP_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
	)
	MCP_MAX_CONCURRENT_REQUESTS: int = int(
		os.getenv("MCP_MAX_CONCURRENT_REQUESTS", "100")
	)
	MCP_REQUEST_TIMEOUT: int = int(os.getenv("MCP_REQUEST_TIMEOUT", "60"))
	MCP_ENABLE_AI_INSIGHTS: bool = (
		os.getenv("MCP_ENABLE_AI_INSIGHTS", "true").lower() == "true"
	)
	MCP_AI_MODEL_TIMEOUT: int = int(os.getenv("MCP_AI_MODEL_TIMEOUT", "30"))

	@classmethod
	def get_database_url(cls) -> str:
		"""Generate database URL for async connections."""
		return f"postgresql+asyncpg://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

	@classmethod
	def get_asyncpg_url(cls) -> str:
		"""Generate asyncpg connection URL."""
		return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

	@classmethod
	def validate_required_vars(cls) -> list[str]:
		"""Validate that all required environment variables are set."""
		missing_vars = []

		if not cls.OPENAI_API_KEY:
			missing_vars.append("OPENAI_API_KEY")

		return missing_vars

	@classmethod
	def get_all_vars(cls) -> dict[str, Any]:
		"""Get all environment variables as a dictionary."""
		return {
			"DB_USER": cls.DB_USER,
			"DB_PASSWORD": cls.DB_PASSWORD,
			"DB_HOST": cls.DB_HOST,
			"DB_PORT": cls.DB_PORT,
			"DB_NAME": cls.DB_NAME,
			"database_url": cls.get_database_url(),
			"APP_NAME": cls.APP_NAME,
			"APP_VERSION": cls.APP_VERSION,
			"DEBUG": cls.DEBUG,
			"LOG_LEVEL": cls.LOG_LEVEL,
			"OPENAI_API_KEY": cls.OPENAI_API_KEY,
			"OPENAI_MODEL": cls.OPENAI_MODEL,
			"MCP_SERVER_NAME": cls.MCP_SERVER_NAME,
			"MCP_SERVER_VERSION": cls.MCP_SERVER_VERSION,
			"MCP_MAX_TOOLS_PER_REQUEST": cls.MCP_MAX_TOOLS_PER_REQUEST,
			"MCP_DEFAULT_TOOL_TIMEOUT": cls.MCP_DEFAULT_TOOL_TIMEOUT,
			"MCP_LOG_LEVEL": cls.MCP_LOG_LEVEL,
			"MCP_LOG_FORMAT": cls.MCP_LOG_FORMAT,
			"MCP_MAX_CONCURRENT_REQUESTS": cls.MCP_MAX_CONCURRENT_REQUESTS,
			"MCP_REQUEST_TIMEOUT": cls.MCP_REQUEST_TIMEOUT,
			"MCP_ENABLE_AI_INSIGHTS": cls.MCP_ENABLE_AI_INSIGHTS,
			"MCP_AI_MODEL_TIMEOUT": cls.MCP_AI_MODEL_TIMEOUT,
		}

	@classmethod
	def print_config(cls, hide_sensitive: bool = True) -> None:
		"""Print current configuration (optionally hiding sensitive data)."""
		config = cls.get_all_vars()

		if hide_sensitive:
			sensitive_keys = ["DB_PASSWORD", "OPENAI_API_KEY"]
			for key in sensitive_keys:
				if key in config:
					config[key] = "***HIDDEN***"

		logger.info("Current Environment Configuration:")
		logger.info("=" * 50)
		for key, value in config.items():
			logger.info(f"{key}: {value}")
		logger.info("=" * 50)


env = EnvConfig()


def get_env_var(key: str, default: str | None = None) -> str:
	"""Get environment variable with optional default."""
	return os.getenv(key, default or "")


def set_env_var(key: str, value: str) -> None:
	"""Set environment variable."""
	os.environ[key] = value


def validate_environment() -> bool:
	"""Validate that all required environment variables are set."""
	missing_vars = env.validate_required_vars()

	if missing_vars:
		logger.warning(
			f"Missing required environment variables: {', '.join(missing_vars)}"
		)
		return False

	return True


if __name__ == "__main__":
	env.print_config()
	validate_environment()
