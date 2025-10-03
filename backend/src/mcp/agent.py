"""AI Agent that uses OpenAI with MCP (Model Context Protocol) for enhanced capabilities."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.errors.error_handler import ErrorHandler
from src.errors.exceptions import MCPError, QueryProcessingError, ValidationError
from src.llm_service import LLMService
from src.mcp.mcp_client import mcp_client
from src.validation.query_validator import QueryValidator


class DataBotAgent:
	"""AI Agent that processes natural language queries using MCP and OpenAI."""

	def __init__(self, db: AsyncSession):
		"""Initialize the agent with database session."""
		self.db = db
		self.llm_service = LLMService()
		self.mcp_client = mcp_client
		self.validator = QueryValidator()
		self.error_handler = ErrorHandler()

	async def process_query(self, user_query: str, model: str | None = None) -> dict:
		"""Process a natural language query using MCP and OpenAI.

		Args:
			user_query: Natural language query from the user
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)

		Returns:
			Dictionary with answer and data

		"""
		validation_result = self.validator.validate_query(user_query)
		if not validation_result.is_valid:
			raise ValidationError("Query validation failed", validation_result.errors)

		sanitized_query = validation_result.sanitized_query

		if validation_result.warnings:
			logger = logging.getLogger(__name__)
			logger.warning(f"Query warnings: {validation_result.warnings}")

		try:
			await self.mcp_client.connect()
		except Exception as e:
			raise MCPError(f"Failed to connect to MCP server: {str(e)}") from e

		try:
			mcp_tools = await self.mcp_client.list_tools()

			result = await self.llm_service.process_with_tools(
				user_query=sanitized_query,
				mcp_tools=mcp_tools,
				mcp_client=self.mcp_client,
				model=model,
			)

			return result
		except ValidationError:
			raise
		except MCPError:
			raise
		except Exception as e:
			raise QueryProcessingError(
				f"An error occurred while processing your query: {str(e)}"
			) from e
