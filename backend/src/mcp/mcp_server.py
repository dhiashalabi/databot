"""MCP Server implementation."""

import asyncio
import logging
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from src.config import Settings
from src.errors.error_handler import ErrorHandler
from src.errors.exceptions import DatabaseError, MCPError
from src.mcp.insights import AIInsightsEngine
from src.mcp.tools import MCPTools

from .cache import ToolCache
from .handlers import ResourceHandler, ToolHandler
from .registry import ToolRegistry
from .security import DataSanitizer

logger = logging.getLogger(__name__)


class MCPServer:
	"""MCP Server using modularized architecture."""

	def __init__(self, settings: Settings | None = None):
		"""Initialize the MCP server with modular components."""
		self.settings = settings or Settings()
		self.server = Server("databot-mcp-server")

		self.error_handler = ErrorHandler()
		self.data_tools: MCPTools | None = None
		self.insights_engine: AIInsightsEngine | None = None
		self.tool_registry: ToolRegistry | None = None
		self.tool_handler: ToolHandler | None = None
		self.resource_handler: ResourceHandler | None = None
		self.db_session = None

		self.tool_cache: ToolCache | None = None
		self.data_sanitizer: DataSanitizer | None = None

		self._is_healthy = False
		self._last_health_check = None

		self._setup_handlers()

	def _setup_handlers(self):
		"""Setup MCP server handlers using modular components."""

		@self.server.list_tools()
		async def handle_list_tools(
			group: str = None, category: str = None, namespace: str = None
		):
			"""List available tools using modular tool handler with optional filtering."""
			try:
				if not self.tool_handler:
					await self._initialize_components()

				return await self.tool_handler.list_tools(
					group=group, category=category, namespace=namespace
				)

			except Exception as e:
				error_response = self.error_handler.handle_error(
					e, {"context": "list_tools", "operation": "mcp_server"}
				)
				logger.error(f"Error listing tools: {error_response}")
				raise MCPError(f"Failed to list tools: {str(e)}") from e

		@self.server.call_tool()
		async def handle_call_tool(name: str, arguments: dict[str, Any]):
			"""Handle tool calls using modular tool handler with caching and timeout guards."""
			try:
				if not self.tool_handler:
					await self._initialize_components()

				if self.tool_cache and self._is_cacheable_tool(name):
					cached_result = await self.tool_cache.get(name, arguments)
					if cached_result is not None:
						return self._sanitize_result(cached_result)

				timeout = self._get_tool_timeout(name)
				result = await asyncio.wait_for(
					self.tool_handler.call_tool(name, arguments), timeout=timeout
				)

				if self.tool_cache and self._is_cacheable_tool(name):
					await self.tool_cache.set(name, arguments, result)

				return self._sanitize_result(result)

			except TimeoutError as e:
				logger.error(f"Tool execution timed out: {name}")
				raise MCPError(
					f"Tool execution timed out after {timeout}s: {name}"
				) from e
			except Exception as e:
				error_response = self.error_handler.handle_error(
					e,
					{
						"context": "call_tool",
						"tool_name": name,
						"arguments": arguments,
						"operation": "mcp_server",
					},
				)
				logger.error(f"Error calling tool {name}: {error_response}")
				raise MCPError(f"Tool execution failed: {str(e)}") from e

		@self.server.list_resources()
		async def handle_list_resources():
			"""List available resources using modular resource handler."""
			try:
				if not self.resource_handler:
					await self._initialize_components()

				return await self.resource_handler.list_resources()

			except Exception as e:
				error_response = self.error_handler.handle_error(
					e, {"context": "list_resources", "operation": "mcp_server"}
				)
				logger.error(f"Error listing resources: {error_response}")
				raise MCPError(f"Failed to list resources: {str(e)}") from e

		@self.server.read_resource()
		async def handle_read_resource(uri: str):
			"""Read resource using modular resource handler."""
			try:
				if not self.resource_handler:
					await self._initialize_components()

				return await self.resource_handler.read_resource(uri)

			except Exception as e:
				error_response = self.error_handler.handle_error(
					e,
					{"context": "read_resource", "uri": uri, "operation": "mcp_server"},
				)
				logger.error(f"Error reading resource {uri}: {error_response}")
				raise MCPError(f"Failed to read resource: {str(e)}") from e

	async def _initialize_components(self):
		"""Initialize all modular components."""
		try:
			await self._initialize_database()

			self.tool_cache = ToolCache(
				default_ttl=self.settings.cache_ttl
				if hasattr(self.settings, "cache_ttl")
				else 300,
				max_size=self.settings.cache_max_size
				if hasattr(self.settings, "cache_max_size")
				else 1000,
			)
			self.data_sanitizer = DataSanitizer()

			await self.tool_cache.start_cleanup_task()

			self.tool_registry = ToolRegistry(self.data_tools, self.insights_engine)

			self.tool_handler = ToolHandler(self.tool_registry, self.data_sanitizer)
			self.resource_handler = ResourceHandler(self.tool_registry)

			self._is_healthy = True

		except Exception as e:
			self._is_healthy = False
			raise DatabaseError(f"Failed to initialize MCP components: {str(e)}") from e

	async def _initialize_database(self):
		"""Initialize database using enhanced database.py."""
		from src.database import get_session_maker, initialize_database

		try:
			await initialize_database()

			session_maker = await get_session_maker()
			self.db_session = session_maker()

			self.data_tools = MCPTools(self.db_session)
			self.insights_engine = AIInsightsEngine(self.db_session)
		except Exception as e:
			raise DatabaseError(f"Database initialization failed: {str(e)}") from e

	async def health_check(self) -> dict[str, Any]:
		"""Health check following existing patterns."""
		try:
			from src.database import health_check as db_health_check

			db_health = await db_health_check()
			if db_health["status"] != "healthy":
				return {
					"status": "unhealthy",
					"reason": f"Database: {db_health['message']}",
					"components": {
						"database": "unhealthy",
						"tools": "unavailable",
						"cache": "disabled",
						"sanitizer": "disabled",
					},
				}

			if not self.data_tools:
				return {"status": "unhealthy", "reason": "Data tools not initialized"}

			await self.data_tools.get_sales_summary()

			self._is_healthy = True
			self._last_health_check = asyncio.get_event_loop().time()

			return {
				"status": "healthy",
				"timestamp": self._last_health_check,
				"components": {
					"database": "connected",
					"tools": "available",
					"cache": "active" if self.tool_cache else "disabled",
					"sanitizer": "active" if self.data_sanitizer else "disabled",
				},
			}

		except Exception as e:
			self._is_healthy = False
			error_response = self.error_handler.handle_error(
				e, {"context": "health_check", "operation": "mcp_server"}
			)
			logger.error(f"Health check failed: {error_response}")
			return {"status": "unhealthy", "reason": str(e)}

	async def run(self):
		"""Run the MCP server."""
		try:
			async with stdio_server() as (read_stream, write_stream):
				await self.server.run(
					read_stream,
					write_stream,
					InitializationOptions(
						server_name="databot-mcp-server",
						server_version="1.0.0",
						capabilities=self.server.get_capabilities(
							notification_options=NotificationOptions(),
							experimental_capabilities={},
						),
					),
				)
		except Exception as e:
			error_response = self.error_handler.handle_error(
				e, {"context": "server_run", "operation": "mcp_server"}
			)
			logger.error(f"Server run error: {error_response}")
			raise MCPError(f"Server failed to run: {str(e)}") from e
		finally:
			await self.cleanup()

	def _is_cacheable_tool(self, tool_name: str) -> bool:
		"""Check if a tool should be cached based on its name."""
		cacheable_tools = {
			"get_sales_summary",
			"get_revenue_by_channel",
			"get_sales_trends",
			"get_top_selling_products",
			"get_customer_segmentation",
			"get_customer_lifetime_value",
			"get_product_performance_analysis",
			"get_category_performance",
			"get_invoice_analysis",
			"get_ai_insights",
			"get_sales_forecast",
		}
		return tool_name in cacheable_tools

	def _get_tool_timeout(self, tool_name: str) -> int:
		"""Get timeout for a specific tool in seconds."""
		timeouts = {
			"get_ai_insights": 30,
			"get_sales_forecast": 20,
			"get_customer_segmentation": 15,
			"get_product_performance_analysis": 15,
			"get_category_performance": 15,
			"get_invoice_analysis": 15,
		}
		return timeouts.get(tool_name, 10)

	def _sanitize_result(self, result: Any) -> Any:
		"""Sanitize sensitive data in tool results."""
		if not self.data_sanitizer:
			return result

		try:
			return self.data_sanitizer.sanitize_data(result)
		except Exception:
			return result

	async def cleanup(self):
		"""Clean up database session and resources."""
		try:
			if self.db_session:
				await self.db_session.close()
				self.db_session = None

			if self.tool_cache:
				await self.tool_cache.invalidate_all()

			from src.database import close_db

			await close_db()

			self.data_tools = None
			self.insights_engine = None
			self.tool_registry = None
			self.tool_handler = None
			self.resource_handler = None
			self.tool_cache = None
			self.data_sanitizer = None
			self._is_healthy = False

		except Exception as e:
			error_response = self.error_handler.handle_error(
				e, {"context": "cleanup", "operation": "mcp_server"}
			)
			logger.error(f"Cleanup error: {error_response}")


async def main():
	"""Main entry point for the MCP server."""
	settings = Settings()

	server = MCPServer(settings)

	try:
		await server.run()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		logger.error(f"Server error: {e}")
		raise
	finally:
		await server.cleanup()


if __name__ == "__main__":
	asyncio.run(main())
