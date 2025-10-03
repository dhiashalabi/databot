"""MCP Server implementation for PostgreSQL database operations."""

import asyncio
import json
import logging
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
	ListResourcesResult,
	ListToolsResult,
	Resource,
	TextContent,
	Tool,
)

from src.mcp.insights import AIInsightsEngine
from src.mcp.tools import MCPTools

logger = logging.getLogger(__name__)


class MCPServer:
	"""MCP Server for PostgreSQL operations."""

	def __init__(self):
		self.server = Server("databot-mcp-server")
		self.data_tools: MCPTools | None = None
		self.insights_engine: AIInsightsEngine | None = None
		self.db_session = None
		self._setup_handlers()

	def _setup_handlers(self):
		"""Setup MCP server handlers."""

		@self.server.list_tools()
		async def handle_list_tools() -> ListToolsResult:
			"""List available tools."""
			return ListToolsResult(
				tools=[
					Tool(
						name="get_sales_analytics",
						description="Get comprehensive sales analytics with AI-powered insights",
						inputSchema={
							"type": "object",
							"properties": {
								"start_date": {"type": "string", "format": "date"},
								"end_date": {"type": "string", "format": "date"},
								"category": {"type": "string"},
								"include_insights": {
									"type": "boolean",
									"default": True,
								},
							},
							"required": ["start_date", "end_date"],
						},
					),
					Tool(
						name="get_customer_insights",
						description="Get AI-powered customer behavior insights and segmentation",
						inputSchema={
							"type": "object",
							"properties": {
								"customer_id": {"type": "string"},
								"timeframe": {
									"type": "string",
									"enum": ["7d", "30d", "90d", "1y"],
								},
								"include_predictions": {
									"type": "boolean",
									"default": True,
								},
							},
						},
					),
					Tool(
						name="get_product_performance",
						description="Analyze product performance with trend analysis and recommendations",
						inputSchema={
							"type": "object",
							"properties": {
								"product_id": {"type": "string"},
								"period": {
									"type": "string",
									"enum": ["week", "month", "quarter", "year"],
								},
								"include_recommendations": {
									"type": "boolean",
									"default": True,
								},
							},
						},
					),
					Tool(
						name="get_business_insights",
						description="Get comprehensive business insights with AI analysis",
						inputSchema={
							"type": "object",
							"properties": {
								"insight_type": {
									"type": "string",
									"enum": [
										"overview",
										"trends",
										"anomalies",
										"forecast",
									],
								},
								"timeframe": {
									"type": "string",
									"enum": ["7d", "30d", "90d", "1y"],
								},
							},
							"required": ["insight_type"],
						},
					),
					Tool(
						name="compare_periods",
						description="Compare business metrics between two periods with AI analysis",
						inputSchema={
							"type": "object",
							"properties": {
								"period1_start": {"type": "string", "format": "date"},
								"period1_end": {"type": "string", "format": "date"},
								"period2_start": {"type": "string", "format": "date"},
								"period2_end": {"type": "string", "format": "date"},
								"metrics": {
									"type": "array",
									"items": {"type": "string"},
									"default": ["sales", "customers", "products"],
								},
							},
							"required": [
								"period1_start",
								"period1_end",
								"period2_start",
								"period2_end",
							],
						},
					),
					Tool(
						name="get_sales_by_period",
						description="Get total sales for a specific time period",
						inputSchema={
							"type": "object",
							"properties": {
								"start_date": {"type": "string", "format": "date"},
								"end_date": {"type": "string", "format": "date"},
								"category": {"type": "string"},
							},
							"required": ["start_date", "end_date"],
						},
					),
					Tool(
						name="compare_sales_periods",
						description="Compare sales between two time periods",
						inputSchema={
							"type": "object",
							"properties": {
								"period1_start": {"type": "string", "format": "date"},
								"period1_end": {"type": "string", "format": "date"},
								"period2_start": {"type": "string", "format": "date"},
								"period2_end": {"type": "string", "format": "date"},
							},
							"required": [
								"period1_start",
								"period1_end",
								"period2_start",
								"period2_end",
							],
						},
					),
					Tool(
						name="get_top_products",
						description="Get the top selling products ranked by sales amount",
						inputSchema={
							"type": "object",
							"properties": {
								"limit": {"type": "integer", "default": 10},
								"start_date": {"type": "string", "format": "date"},
							},
						},
					),
					Tool(
						name="get_top_customers",
						description="Get top customers ranked by total spending",
						inputSchema={
							"type": "object",
							"properties": {
								"limit": {"type": "integer", "default": 10},
								"start_date": {"type": "string", "format": "date"},
							},
						},
					),
					Tool(
						name="get_products_low_stock",
						description="Get products with stock quantity below a threshold",
						inputSchema={
							"type": "object",
							"properties": {
								"threshold": {"type": "integer", "default": 20},
							},
						},
					),
					Tool(
						name="get_pending_invoices",
						description="Get all pending/unpaid invoices",
						inputSchema={
							"type": "object",
							"properties": {},
						},
					),
					Tool(
						name="get_customer_details",
						description="Get detailed information about a specific customer including contact details, company, and purchase history",
						inputSchema={
							"type": "object",
							"properties": {
								"customer_name": {
									"type": "string",
									"description": "Name of the customer (partial matches supported)",
								},
							},
							"required": ["customer_name"],
						},
					),
					Tool(
						name="get_product_details",
						description="Get detailed information about a specific product including pricing, stock, and performance",
						inputSchema={
							"type": "object",
							"properties": {
								"product_name": {
									"type": "string",
									"description": "Name of the product (partial matches supported)",
								},
								"product_id": {
									"type": "string",
									"description": "ID of the product",
								},
							},
						},
					),
					Tool(
						name="search_customers",
						description="Search customers by various criteria like name, email, company, or customer type",
						inputSchema={
							"type": "object",
							"properties": {
								"search_term": {
									"type": "string",
									"description": "Search term to match against customer name, email, or company",
								},
								"customer_type": {
									"type": "string",
									"enum": ["retail", "wholesale", "corporate"],
									"description": "Filter by customer type",
								},
								"limit": {
									"type": "integer",
									"default": 20,
									"description": "Maximum number of results to return",
								},
							},
						},
					),
					Tool(
						name="search_products",
						description="Search products by name, category, or SKU",
						inputSchema={
							"type": "object",
							"properties": {
								"search_term": {
									"type": "string",
									"description": "Search term to match against product name or SKU",
								},
								"category": {
									"type": "string",
									"description": "Filter by product category",
								},
								"low_stock_only": {
									"type": "boolean",
									"default": False,
									"description": "Only return products with low stock",
								},
								"limit": {
									"type": "integer",
									"default": 20,
									"description": "Maximum number of results to return",
								},
							},
						},
					),
					Tool(
						name="get_customer_purchase_history",
						description="Get detailed purchase history for a specific customer",
						inputSchema={
							"type": "object",
							"properties": {
								"customer_name": {
									"type": "string",
									"description": "Name of the customer",
								},
								"start_date": {
									"type": "string",
									"format": "date",
									"description": "Start date for purchase history",
								},
								"end_date": {
									"type": "string",
									"format": "date",
									"description": "End date for purchase history",
								},
								"limit": {
									"type": "integer",
									"default": 50,
									"description": "Maximum number of purchases to return",
								},
							},
							"required": ["customer_name"],
						},
					),
				]
			)

		@self.server.call_tool()
		async def handle_call_tool(
			name: str, arguments: dict[str, Any]
		) -> list[TextContent]:
			"""Handle tool calls."""
			try:
				if not self.data_tools or not self.insights_engine:
					await self._initialize_database()

				result = await self._execute_tool(name, arguments)

				return [
					TextContent(
						type="text", text=json.dumps(result, indent=2, default=str)
					)
				]
			except Exception as e:
				logger.error(f"Error executing tool {name}: {e}")
				return [TextContent(type="text", text=f"Error: {str(e)}")]

		@self.server.list_resources()
		async def handle_list_resources() -> ListResourcesResult:
			"""List available resources."""
			return ListResourcesResult(
				resources=[
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
			)

		@self.server.read_resource()
		async def handle_read_resource(uri: str) -> list[TextContent]:
			"""Read resource data."""
			try:
				if not self.data_tools:
					await self._initialize_database()

				data = await self._get_resource_data(uri)

				return [
					TextContent(
						type="text", text=json.dumps(data, indent=2, default=str)
					)
				]
			except Exception as e:
				logger.error(f"Error reading resource {uri}: {e}")
				return [TextContent(type="text", text=f"Error: {str(e)}")]

	async def _initialize_database(self):
		"""Initialize database session and tools."""
		from src.database import async_session_maker

		if not self.db_session:
			self.db_session = async_session_maker()
		self.data_tools = MCPTools(self.db_session)
		self.insights_engine = AIInsightsEngine(self.db_session)

	async def _execute_tool(
		self, tool_name: str, arguments: dict[str, Any]
	) -> dict[str, Any]:
		"""Execute a tool with the given arguments."""
		# AI Insights Engine Tools
		if tool_name == "get_sales_analytics":
			return await self.insights_engine.get_sales_analytics(
				start_date=arguments["start_date"],
				end_date=arguments["end_date"],
				category=arguments.get("category"),
				include_insights=arguments.get("include_insights", True),
			)
		elif tool_name == "get_customer_insights":
			return await self.insights_engine.get_customer_insights(
				customer_id=arguments.get("customer_id"),
				timeframe=arguments.get("timeframe", "30d"),
				include_predictions=arguments.get("include_predictions", True),
			)
		elif tool_name == "get_product_performance":
			return await self.insights_engine.get_product_performance(
				product_id=arguments.get("product_id"),
				period=arguments.get("period", "month"),
				include_recommendations=arguments.get("include_recommendations", True),
			)
		elif tool_name == "get_business_insights":
			return await self.insights_engine.get_business_insights(
				insight_type=arguments["insight_type"],
				timeframe=arguments.get("timeframe", "30d"),
			)
		elif tool_name == "compare_periods":
			return await self.insights_engine.compare_periods(
				period1_start=arguments["period1_start"],
				period1_end=arguments["period1_end"],
				period2_start=arguments["period2_start"],
				period2_end=arguments["period2_end"],
				metrics=arguments.get("metrics", ["sales", "customers", "products"]),
			)

		# Database Tools
		elif tool_name == "get_sales_by_period":
			return await self.data_tools.get_sales_by_period(
				start_date=arguments["start_date"],
				end_date=arguments["end_date"],
				category=arguments.get("category"),
			)
		elif tool_name == "compare_sales_periods":
			return await self.data_tools.compare_sales_periods(
				period1_start=arguments["period1_start"],
				period1_end=arguments["period1_end"],
				period2_start=arguments["period2_start"],
				period2_end=arguments["period2_end"],
			)
		elif tool_name == "get_top_products":
			return await self.data_tools.get_top_products(
				limit=arguments.get("limit", 10),
				start_date=arguments.get("start_date"),
			)
		elif tool_name == "get_top_customers":
			return await self.data_tools.get_top_customers(
				limit=arguments.get("limit", 10),
				start_date=arguments.get("start_date"),
			)
		elif tool_name == "get_products_low_stock":
			return await self.data_tools.get_products_low_stock(
				threshold=arguments.get("threshold", 20),
			)
		elif tool_name == "get_pending_invoices":
			return await self.data_tools.get_pending_invoices()
		elif tool_name == "get_customer_details":
			return await self.data_tools.get_customer_details(
				customer_name=arguments["customer_name"]
			)
		elif tool_name == "get_product_details":
			return await self.data_tools.get_product_details(
				product_name=arguments.get("product_name"),
				product_id=arguments.get("product_id"),
			)
		elif tool_name == "search_customers":
			return await self.data_tools.search_customers(
				search_term=arguments.get("search_term"),
				customer_type=arguments.get("customer_type"),
				limit=arguments.get("limit", 20),
			)
		elif tool_name == "search_products":
			return await self.data_tools.search_products(
				search_term=arguments.get("search_term"),
				category=arguments.get("category"),
				low_stock_only=arguments.get("low_stock_only", False),
				limit=arguments.get("limit", 20),
			)
		elif tool_name == "get_customer_purchase_history":
			return await self.data_tools.get_customer_purchase_history(
				customer_name=arguments["customer_name"],
				start_date=arguments.get("start_date"),
				end_date=arguments.get("end_date"),
				limit=arguments.get("limit", 50),
			)
		else:
			raise ValueError(f"Unknown tool: {tool_name}")

	async def _get_resource_data(self, uri: str) -> dict[str, Any]:
		"""Get data for a specific resource URI."""
		if uri == "databot://sales":
			return await self.data_tools.get_sales_summary()
		elif uri == "databot://customers":
			return await self.data_tools.get_customers_summary()
		elif uri == "databot://products":
			return await self.data_tools.get_products_summary()
		else:
			raise ValueError(f"Unknown resource: {uri}")

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
		finally:
			await self.cleanup()

	async def cleanup(self):
		"""Clean up database session."""
		if self.db_session:
			await self.db_session.close()


async def main():
	"""Main entry point for the MCP server."""
	server = MCPServer()
	await server.run()


if __name__ == "__main__":
	asyncio.run(main())
