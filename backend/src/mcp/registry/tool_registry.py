"""Tool registry for managing MCP tool execution and routing."""

from collections.abc import Callable
import logging
from typing import Any

from mcp.types import Tool

from .tool_definitions import ToolDefinitions

logger = logging.getLogger(__name__)


class ToolRegistry:
	"""Registry for managing MCP tool definitions and execution."""

	TOOL_GROUPS = {
		"ai": "insights_engine",
		"sales": "data_tools",
		"customers": "data_tools",
		"products": "data_tools",
		"invoices": "data_tools",
		"analytics": "data_tools",
		"charts": "data_tools",
		"files": "file_tools",
		"discovery": "self",
	}

	def __init__(self, data_tools, insights_engine):
		"""Initialize the tool registry with tool execution."""
		self.data_tools = data_tools
		self.insights_engine = insights_engine
		self.file_tools = data_tools
		self.tool_definitions = ToolDefinitions()
		self._tool_metadata = self.tool_definitions.get_tool_metadata()
		self._namespace_aliases = self.tool_definitions.get_namespace_aliases()

	def get_all_tools(self) -> list[Tool]:
		"""Get all available tools."""
		return self.tool_definitions.get_all_tools()

	def get_tools_by_group(self, group: str) -> list[Tool]:
		"""Get tools filtered by group."""
		return self.tool_definitions.get_tools_by_group(group)

	def get_tools_by_category(self, category: str) -> list[Tool]:
		"""Get tools filtered by category."""
		return self.tool_definitions.get_tools_by_category(category)

	def get_tools_by_namespace(self, namespace: str) -> list[Tool]:
		"""Get tools filtered by namespace."""
		return self.tool_definitions.get_tools_by_namespace(namespace)

	def get_tools_filtered(
		self,
		group: str | None = None,
		category: str | None = None,
		namespace: str | None = None,
	) -> list[Tool]:
		"""Get tools with optional filtering by group, category, or namespace."""
		all_tools = self.tool_definitions.get_all_tools()
		metadata = self.tool_definitions.get_tool_metadata()

		filtered_tools = []
		for tool in all_tools:
			tool_meta = metadata.get(tool.name, {})

			if group and tool_meta.get("group") != group:
				continue
			if category and tool_meta.get("category") != category:
				continue
			if namespace and tool_meta.get("namespace") != namespace:
				continue

			filtered_tools.append(tool)

		return filtered_tools

	def get_namespace_aliases(self) -> dict[str, str]:
		"""Get namespace aliases."""
		return self.tool_definitions.get_namespace_aliases()

	def get_available_groups(self) -> list[str]:
		"""Get list of available tool groups."""
		return self.tool_definitions.get_available_groups()

	def get_available_categories(self) -> list[str]:
		"""Get list of available tool categories."""
		return self.tool_definitions.get_available_categories()

	def get_available_namespaces(self) -> list[str]:
		"""Get list of available tool namespaces."""
		return self.tool_definitions.get_available_namespaces()

	def _get_tool_executor(self, tool_name: str) -> Callable:
		"""Get the appropriate executor for a tool based on its group."""
		actual_tool_name = self._namespace_aliases.get(tool_name, tool_name)

		tool_meta = self._tool_metadata.get(actual_tool_name, {})
		group = tool_meta.get("group")

		if not group:
			raise ValueError(f"Unknown tool: {tool_name}")

		executor_type = self.TOOL_GROUPS.get(group)
		if not executor_type:
			raise ValueError(f"Unknown tool group: {group}")

		if executor_type == "self":
			return self._execute_discovery_tool
		else:
			executor = getattr(self, executor_type)
			return self._create_dynamic_executor(executor, actual_tool_name)

	def _create_dynamic_executor(self, executor, tool_name: str) -> Callable:
		"""Create a dynamic executor that calls the appropriate method on the executor."""

		async def dynamic_executor(
			tool_name: str, arguments: dict[str, Any]
		) -> dict[str, Any]:
			if hasattr(executor, tool_name):
				method = getattr(executor, tool_name)
				return await method(**arguments)
			else:
				raise ValueError(
					f"Method {tool_name} not found on {type(executor).__name__}"
				)

		return dynamic_executor

	async def execute_tool(
		self, tool_name: str, arguments: dict[str, Any]
	) -> dict[str, Any]:
		"""Execute a tool with the given arguments."""
		try:
			executor = self._get_tool_executor(tool_name)
			return await executor(tool_name, arguments)
		except Exception as e:
			logger.error(f"Error executing tool {tool_name}: {e}")
			raise

	async def _execute_discovery_tool(
		self, tool_name: str, arguments: dict[str, Any]
	) -> dict[str, Any]:
		"""Execute discovery tools."""
		if tool_name == "get_tool_groups":
			groups = self.get_available_groups()
			result = {}
			for group in groups:
				tools = self.get_tools_by_group(group)
				result[group] = [tool.name for tool in tools]
			return result
		elif tool_name == "get_tool_categories":
			categories = self.get_available_categories()
			result = {}
			for category in categories:
				tools = self.get_tools_by_category(category)
				result[category] = [tool.name for tool in tools]
			return result
		elif tool_name == "get_tool_namespaces":
			return self.get_namespace_aliases()
		elif tool_name == "get_tool_metadata":
			return self.tool_definitions.get_tool_metadata()
		else:
			raise ValueError(f"Unknown discovery tool: {tool_name}")
