"""Server configuration for MCP server."""

from dataclasses import dataclass
from typing import Any

from src.env import env


@dataclass
class ServerConfig:
	"""Configuration for MCP server."""

	server_name: str = env.MCP_SERVER_NAME
	server_version: str = env.MCP_SERVER_VERSION

	max_tools_per_request: int = env.MCP_MAX_TOOLS_PER_REQUEST
	default_tool_timeout: int = env.MCP_DEFAULT_TOOL_TIMEOUT

	log_level: str = env.MCP_LOG_LEVEL
	log_format: str = env.MCP_LOG_FORMAT

	max_concurrent_requests: int = env.MCP_MAX_CONCURRENT_REQUESTS
	request_timeout: int = env.MCP_REQUEST_TIMEOUT

	enable_ai_insights: bool = env.MCP_ENABLE_AI_INSIGHTS
	ai_model_timeout: int = env.MCP_AI_MODEL_TIMEOUT

	def to_dict(self) -> dict[str, Any]:
		"""Convert configuration to dictionary."""
		return {
			"server_name": self.server_name,
			"server_version": self.server_version,
			"max_tools_per_request": self.max_tools_per_request,
			"default_tool_timeout": self.default_tool_timeout,
			"log_level": self.log_level,
			"log_format": self.log_format,
			"max_concurrent_requests": self.max_concurrent_requests,
			"request_timeout": self.request_timeout,
			"enable_ai_insights": self.enable_ai_insights,
			"ai_model_timeout": self.ai_model_timeout,
		}

	@classmethod
	def from_dict(cls, config_dict: dict[str, Any]) -> "ServerConfig":
		"""Create configuration from dictionary."""
		return cls(**config_dict)

	@classmethod
	def default(cls) -> "ServerConfig":
		"""Get default configuration."""
		return cls()
