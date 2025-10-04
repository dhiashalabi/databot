"""Resource handler for MCP server - manages resource listing and reading."""

import json
import logging
from typing import Any

from mcp.types import ListResourcesResult, Resource, TextContent

from src.mcp.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ResourceHandler:
	"""Handler for MCP resource operations."""

	def __init__(self, tool_registry: ToolRegistry):
		"""Initialize the resource handler."""
		self.tool_registry = tool_registry

	async def list_resources(self) -> ListResourcesResult:
		"""List all available resources."""
		try:
			resources = [
				Resource(
					uri="databot://sales",
					name="Sales Data",
					description="Real-time sales data with analytics",
					mimeType="application/json",
				),
				Resource(
					uri="databot://customers",
					name="Customer Data",
					description="Customer information and behavior data",
					mimeType="application/json",
				),
				Resource(
					uri="databot://products",
					name="Product Catalog",
					description="Product information and performance data",
					mimeType="application/json",
				),
			]
			return ListResourcesResult(resources=resources)
		except Exception as e:
			logger.error(f"Error listing resources: {e}")
			return ListResourcesResult(resources=[])

	async def read_resource(self, uri: str) -> list[TextContent]:
		"""Read data for a specific resource URI."""
		try:
			data = await self._get_resource_data(uri)
			return [
				TextContent(type="text", text=json.dumps(data, indent=2, default=str))
			]
		except Exception as e:
			logger.error(f"Error reading resource {uri}: {e}")
			return [TextContent(type="text", text=f"Error: {str(e)}")]

	async def _get_resource_data(self, uri: str) -> dict[str, Any]:
		"""Get data for a specific resource URI."""
		if uri == "databot://sales":
			return await self.tool_registry.data_tools.get_sales_summary()
		elif uri == "databot://customers":
			return await self.tool_registry.data_tools.get_customers_summary()
		elif uri == "databot://products":
			return await self.tool_registry.data_tools.get_products_summary()
		else:
			raise ValueError(f"Unknown resource: {uri}")
