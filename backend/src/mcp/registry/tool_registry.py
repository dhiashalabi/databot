"""Tool registry for managing MCP tool execution and routing."""

from collections.abc import Callable
import logging
from typing import Any

from mcp.types import Tool

from .tool_definitions import ToolDefinitions

logger = logging.getLogger(__name__)


class ToolRegistry:
	"""Registry for managing MCP tool definitions and execution."""

	def __init__(self, data_tools, insights_engine):
		"""Initialize the tool registry with tool execution."""
		self.data_tools = data_tools
		self.insights_engine = insights_engine
		self.tool_definitions = ToolDefinitions()
		self._execution_map = self._build_execution_map()

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
		self, group: str = None, category: str = None, namespace: str = None
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

	def _build_execution_map(self) -> dict[str, Callable]:
		"""Build the tool execution mapping with namespace aliases."""
		base_map = {
			"get_sales_analytics": self._execute_insights_tool,
			"get_customer_insights": self._execute_insights_tool,
			"get_product_performance": self._execute_insights_tool,
			"get_business_insights": self._execute_insights_tool,
			"compare_periods": self._execute_insights_tool,
			"get_sales_by_period": self._execute_data_tool,
			"compare_sales_periods": self._execute_data_tool,
			"get_sales_by_category": self._execute_data_tool,
			"get_sales_summary": self._execute_data_tool,
			"get_all_sales": self._execute_data_tool,
			"get_sales": self._execute_data_tool,
			"get_sales_trends": self._execute_data_tool,
			"get_top_selling_products": self._execute_data_tool,
			"get_sales_by_channel": self._execute_data_tool,
			"get_sales_forecast": self._execute_data_tool,
			"get_revenue_by_channel": self._execute_data_tool,
			"get_top_customers": self._execute_data_tool,
			"get_customer_details": self._execute_data_tool,
			"get_customers_summary": self._execute_data_tool,
			"search_customers": self._execute_data_tool,
			"get_customer_purchase_history": self._execute_data_tool,
			"get_customers": self._execute_data_tool,
			"get_customer_segmentation": self._execute_data_tool,
			"get_customer_lifetime_value": self._execute_data_tool,
			"get_top_products": self._execute_data_tool,
			"get_products_low_stock": self._execute_data_tool,
			"get_products_summary": self._execute_data_tool,
			"get_product_details": self._execute_data_tool,
			"search_products": self._execute_data_tool,
			"get_products": self._execute_data_tool,
			"get_categories": self._execute_data_tool,
			"get_product_performance_analysis": self._execute_data_tool,
			"get_pending_invoices": self._execute_data_tool,
			"get_invoice_summary": self._execute_data_tool,
			"get_invoices": self._execute_data_tool,
			"get_invoice_analysis": self._execute_data_tool,
			"get_inventory_analysis": self._execute_data_tool,
			"get_category_performance": self._execute_data_tool,
			"get_revenue_analysis": self._execute_data_tool,
			"get_tool_groups": self._execute_discovery_tool,
			"get_tool_categories": self._execute_discovery_tool,
			"get_tool_namespaces": self._execute_discovery_tool,
			"get_tool_metadata": self._execute_discovery_tool,
		}

		namespace_aliases = self.get_namespace_aliases()
		for namespace, original_name in namespace_aliases.items():
			if original_name in base_map:
				base_map[namespace] = base_map[original_name]

		return base_map

	async def execute_tool(
		self, tool_name: str, arguments: dict[str, Any]
	) -> dict[str, Any]:
		"""Execute a tool with the given arguments."""
		if tool_name not in self._execution_map:
			raise ValueError(f"Unknown tool: {tool_name}")

		try:
			execution_func = self._execution_map[tool_name]
			return await execution_func(tool_name, arguments)
		except Exception as e:
			logger.error(f"Error executing tool {tool_name}: {e}")
			raise

	async def _execute_insights_tool(
		self, tool_name: str, arguments: dict[str, Any]
	) -> dict[str, Any]:
		"""Execute AI insights engine tool."""
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
		else:
			raise ValueError(f"Unknown insights tool: {tool_name}")

	async def _execute_data_tool(
		self, tool_name: str, arguments: dict[str, Any]
	) -> dict[str, Any]:
		"""Execute data tools method."""
		if tool_name == "get_sales_by_period":
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
		elif tool_name == "get_sales_by_category":
			return await self.data_tools.get_sales_by_category(
				start_date=arguments.get("start_date"),
			)
		elif tool_name == "get_sales_summary":
			return await self.data_tools.get_sales_summary()
		elif tool_name == "get_all_sales":
			return await self.data_tools.get_all_sales()
		elif tool_name == "get_sales":
			return await self.data_tools.get_sales(
				filters=arguments.get("filters"),
				order_by=arguments.get("order_by"),
				limit=arguments.get("limit"),
				offset=arguments.get("offset", 0),
			)
		elif tool_name == "get_sales_trends":
			return await self.data_tools.get_sales_trends(
				start_date=arguments["start_date"],
				end_date=arguments["end_date"],
				group_by=arguments.get("group_by", "day"),
				category=arguments.get("category"),
			)
		elif tool_name == "get_top_selling_products":
			return await self.data_tools.get_top_selling_products(
				start_date=arguments["start_date"],
				end_date=arguments["end_date"],
				limit=arguments.get("limit", 10),
				category=arguments.get("category"),
			)
		elif tool_name == "get_sales_by_channel":
			return await self.data_tools.get_sales_by_channel(
				start_date=arguments["start_date"],
				end_date=arguments["end_date"],
			)
		elif tool_name == "get_sales_forecast":
			return await self.data_tools.get_sales_forecast(
				periods=arguments.get("months_ahead", 3),
				period_type="month",
			)
		elif tool_name == "get_revenue_by_channel":
			return await self.data_tools.get_revenue_by_channel(
				start_date=arguments.get("start_date"),
			)

		elif tool_name == "get_top_customers":
			return await self.data_tools.get_top_customers(
				limit=arguments.get("limit", 10),
			)
		elif tool_name == "get_customer_details":
			return await self.data_tools.get_customer_details(
				customer_name=arguments["customer_name"]
			)
		elif tool_name == "get_customers_summary":
			return await self.data_tools.get_customers_summary()
		elif tool_name == "search_customers":
			return await self.data_tools.search_customers(
				search_term=arguments.get("search_term"),
				customer_type=arguments.get("customer_type"),
				limit=arguments.get("limit", 20),
			)
		elif tool_name == "get_customer_purchase_history":
			return await self.data_tools.get_customer_purchase_history(
				customer_id=arguments.get("customer_id"),
				limit=arguments.get("limit", 50),
			)
		elif tool_name == "get_customers":
			return await self.data_tools.get_customers(
				filters=arguments.get("filters"),
				order_by=arguments.get("order_by"),
				limit=arguments.get("limit"),
				offset=arguments.get("offset", 0),
			)
		elif tool_name == "get_customer_segmentation":
			return await self.data_tools.get_customer_segmentation()
		elif tool_name == "get_customer_lifetime_value":
			return await self.data_tools.get_customer_lifetime_value(
				customer_id=arguments.get("customer_id"),
			)

		elif tool_name == "get_top_products":
			return await self.data_tools.get_top_products(
				limit=arguments.get("limit", 10),
			)
		elif tool_name == "get_products_low_stock":
			return await self.data_tools.get_products_low_stock(
				threshold=arguments.get("threshold", 20),
			)
		elif tool_name == "get_products_summary":
			return await self.data_tools.get_products_summary()
		elif tool_name == "get_product_details":
			return await self.data_tools.get_product_details(
				product_id=arguments.get("product_id"),
				product_name=arguments.get("product_name"),
			)
		elif tool_name == "search_products":
			return await self.data_tools.search_products(
				search_term=arguments.get("search_term"),
				category=arguments.get("category"),
				low_stock_only=arguments.get("low_stock_only", False),
				limit=arguments.get("limit", 20),
			)
		elif tool_name == "get_products":
			return await self.data_tools.get_products(
				filters=arguments.get("filters"),
				order_by=arguments.get("order_by"),
				limit=arguments.get("limit"),
				offset=arguments.get("offset", 0),
			)
		elif tool_name == "get_categories":
			return await self.data_tools.get_categories(
				filters=arguments.get("filters"),
				order_by=arguments.get("order_by"),
				limit=arguments.get("limit"),
				offset=arguments.get("offset", 0),
			)
		elif tool_name == "get_product_performance_analysis":
			return await self.data_tools.get_product_performance_analysis(
				product_id=arguments.get("product_id"),
			)

		elif tool_name == "get_pending_invoices":
			return await self.data_tools.get_pending_invoices()
		elif tool_name == "get_invoice_summary":
			return await self.data_tools.get_invoice_summary(
				start_date=arguments.get("start_date"),
			)
		elif tool_name == "get_invoices":
			return await self.data_tools.get_invoices(
				filters=arguments.get("filters"),
				order_by=arguments.get("order_by"),
				limit=arguments.get("limit"),
				offset=arguments.get("offset", 0),
			)
		elif tool_name == "get_invoice_analysis":
			return await self.data_tools.get_invoice_analysis()

		elif tool_name == "get_inventory_analysis":
			return await self.data_tools.get_inventory_analysis(
				include_inactive=arguments.get("include_inactive", False),
			)
		elif tool_name == "get_category_performance":
			return await self.data_tools.get_category_performance()
		elif tool_name == "get_revenue_analysis":
			return await self.data_tools.get_revenue_analysis(
				start_date=arguments["start_date"],
				end_date=arguments["end_date"],
				group_by=arguments.get("group_by", "month"),
			)
		else:
			raise ValueError(f"Unknown data tool: {tool_name}")

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
