"""Tool handler for MCP server - manages tool listing and execution."""

import json
import logging
from typing import Any

from mcp.types import ListToolsResult, TextContent

from ..registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolHandler:
	"""Handler for MCP tool operations."""

	def __init__(self, tool_registry: ToolRegistry):
		"""Initialize the tool handler."""
		self.tool_registry = tool_registry

	async def list_tools(
		self, group: str = None, category: str = None, namespace: str = None
	) -> ListToolsResult:
		"""List available tools with optional filtering."""
		try:
			if group or category or namespace:
				tools = self.tool_registry.get_tools_filtered(
					group=group, category=category, namespace=namespace
				)
			else:
				tools = self.tool_registry.get_all_tools()
			return ListToolsResult(tools=tools)
		except Exception as e:
			logger.error(f"Error listing tools: {e}")
			return ListToolsResult(tools=[])

	async def list_tools_by_group(self, group: str) -> ListToolsResult:
		"""List tools filtered by group."""
		try:
			tools = self.tool_registry.get_tools_by_group(group)
			return ListToolsResult(tools=tools)
		except Exception as e:
			logger.error(f"Error listing tools by group {group}: {e}")
			return ListToolsResult(tools=[])

	async def list_tools_by_category(self, category: str) -> ListToolsResult:
		"""List tools filtered by category."""
		try:
			tools = self.tool_registry.get_tools_by_category(category)
			return ListToolsResult(tools=tools)
		except Exception as e:
			logger.error(f"Error listing tools by category {category}: {e}")
			return ListToolsResult(tools=[])

	async def list_tools_by_namespace(self, namespace: str) -> ListToolsResult:
		"""List tools filtered by namespace."""
		try:
			tools = self.tool_registry.get_tools_by_namespace(namespace)
			return ListToolsResult(tools=tools)
		except Exception as e:
			logger.error(f"Error listing tools by namespace {namespace}: {e}")
			return ListToolsResult(tools=[])

	async def get_tool_groups(self) -> dict[str, list[str]]:
		"""Get available tool groups and their tools."""
		try:
			groups = self.tool_registry.get_available_groups()
			result = {}
			for group in groups:
				tools = self.tool_registry.get_tools_by_group(group)
				result[group] = [tool.name for tool in tools]
			return result
		except Exception as e:
			logger.error(f"Error getting tool groups: {e}")
			return {}

	async def get_tool_categories(self) -> dict[str, list[str]]:
		"""Get available tool categories and their tools."""
		try:
			categories = self.tool_registry.get_available_categories()
			result = {}
			for category in categories:
				tools = self.tool_registry.get_tools_by_category(category)
				result[category] = [tool.name for tool in tools]
			return result
		except Exception as e:
			logger.error(f"Error getting tool categories: {e}")
			return {}

	async def get_tool_namespaces(self) -> dict[str, str]:
		"""Get available tool namespaces and their original names."""
		try:
			return self.tool_registry.get_namespace_aliases()
		except Exception as e:
			logger.error(f"Error getting tool namespaces: {e}")
			return {}

	async def call_tool(
		self, name: str, arguments: dict[str, Any]
	) -> list[TextContent]:
		"""Call a tool with the given arguments."""
		try:
			result = await self.tool_registry.execute_tool(name, arguments)
			return [
				TextContent(type="text", text=json.dumps(result, indent=2, default=str))
			]
		except Exception as e:
			logger.error(f"Error executing tool {name}: {e}")
			return [TextContent(type="text", text=f"Error: {str(e)}")]
