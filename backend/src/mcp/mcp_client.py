"""MCP Client for DataBot operations."""

from contextlib import AsyncExitStack
import json
import logging
from typing import Any

from mcp.client.stdio import stdio_client

from mcp import ClientSession, StdioServerParameters

logger = logging.getLogger(__name__)


class MCPClient:
	"""MCP Client for DataBot operations."""

	def __init__(self):
		"""Initialize MCP client."""
		self.session: ClientSession | None = None
		self.exit_stack: AsyncExitStack | None = None
		self._connected = False
		self._server_params = StdioServerParameters(
			command="python",
			args=["-m", "src.mcp.mcp_server"],
		)

	async def connect(self):
		"""Connect to the MCP server."""
		if self._connected and self.session:
			try:
				await self.session.list_tools()
				return
			except Exception:
				self._connected = False
				self.session = None

		await self._connect_to_mcp_server()

	async def _connect_to_mcp_server(self):
		"""Connect to an actual MCP server using stdio transport."""
		try:
			self.exit_stack = AsyncExitStack()

			stdio_transport = await self.exit_stack.enter_async_context(
				stdio_client(self._server_params)
			)

			self.session = await self.exit_stack.enter_async_context(
				ClientSession(stdio_transport[0], stdio_transport[1])
			)

			await self.session.initialize()

			self._connected = True
			logger.info("Connected to MCP server via stdio")

		except Exception as e:
			logger.error(f"Failed to connect to MCP server: {e}")
			await self.close()
			raise

	async def call_tool(
		self, tool_name: str, arguments: dict[str, Any]
	) -> dict[str, Any]:
		"""Call a tool on the MCP server."""
		if not self._connected:
			await self.connect()

		if not self.session:
			raise RuntimeError("MCP session not available")

		try:
			result = await self.session.call_tool(tool_name, arguments)
			if result.content and len(result.content) > 0:
				content = result.content[0]
				if hasattr(content, "text"):
					try:
						return json.loads(content.text)
					except json.JSONDecodeError as json_err:
						logger.error(
							f"JSON decode error for tool {tool_name}: {json_err}"
						)
						logger.error(f"Raw content: {content.text}")
						return {
							"error": f"Invalid JSON response: {str(json_err)}",
							"raw_content": content.text,
						}
				else:
					return {"result": str(content)}
			return {"result": "No content returned"}
		except Exception as e:
			logger.error(f"Error calling MCP tool {tool_name}: {e}")
			raise

	async def list_tools(self) -> list[dict[str, Any]]:
		"""List available tools."""
		if not self._connected:
			await self.connect()

		if not self.session:
			raise RuntimeError("MCP session not available")

		try:
			result = await self.session.list_tools()
			return [tool.model_dump() for tool in result.tools]
		except Exception as e:
			logger.error(f"Error listing MCP tools: {e}")
			raise

	async def list_resources(self) -> list[dict[str, Any]]:
		"""List available resources."""
		if not self._connected:
			await self.connect()

		if not self.session:
			raise RuntimeError("MCP session not available")

		try:
			result = await self.session.list_resources()
			return [resource.model_dump() for resource in result.resources]
		except Exception as e:
			logger.error(f"Error listing MCP resources: {e}")
			raise

	async def read_resource(self, uri: str) -> dict[str, Any]:
		"""Read a resource."""
		if not self._connected:
			await self.connect()

		if not self.session:
			raise RuntimeError("MCP session not available")

		try:
			result = await self.session.read_resource(uri)
			if result.contents and len(result.contents) > 0:
				content = result.contents[0]
				if hasattr(content, "text"):
					try:
						return json.loads(content.text)
					except json.JSONDecodeError as json_err:
						logger.error(
							f"JSON decode error for resource {uri}: {json_err}"
						)
						logger.error(f"Raw content: {content.text}")
						return {
							"error": f"Invalid JSON response: {str(json_err)}",
							"raw_content": content.text,
						}
				else:
					return {"result": str(content)}
			return {"result": "No content returned"}
		except Exception as e:
			logger.error(f"Error reading MCP resource {uri}: {e}")
			raise

	async def close(self):
		"""Close the MCP client connection."""
		if self.exit_stack:
			await self.exit_stack.aclose()
		self._connected = False
		self.session = None
		self.exit_stack = None


mcp_client = MCPClient()
