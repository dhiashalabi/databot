"""Tool definitions for MCP server."""

from mcp.types import Tool


class ToolDefinitions:
	"""Tool definitions and schemas for MCP server."""

	@staticmethod
	def get_ai_insights_tools() -> list[Tool]:
		"""Get AI insights engine tools."""
		return [
			Tool(
				name="get_sales_analytics",
				description="Get comprehensive sales analytics with AI-powered insights",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
						"end_date": {"type": "string", "format": "date"},
						"category": {"type": "string"},
						"include_insights": {"type": "boolean", "default": True},
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
						"include_predictions": {"type": "boolean", "default": True},
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
						"include_recommendations": {"type": "boolean", "default": True},
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
							"enum": ["overview", "trends", "anomalies", "forecast"],
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
		]

	@staticmethod
	def get_sales_tools() -> list[Tool]:
		"""Get sales analytics tools."""
		return [
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
				name="get_sales_by_category",
				description="Get sales breakdown by product category",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
					},
				},
			),
			Tool(
				name="get_sales_summary",
				description="Get overall sales summary statistics",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_sales_trends",
				description="Get sales trends over time with detailed analysis and growth rates",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
						"end_date": {"type": "string", "format": "date"},
						"group_by": {
							"type": "string",
							"enum": ["day", "week", "month", "quarter"],
							"default": "day",
						},
						"category": {"type": "string"},
					},
					"required": ["start_date", "end_date"],
				},
			),
			Tool(
				name="get_top_selling_products",
				description="Get top selling products by revenue and quantity with performance metrics",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
						"end_date": {"type": "string", "format": "date"},
						"limit": {"type": "integer", "default": 10},
						"category": {"type": "string"},
					},
					"required": ["start_date", "end_date"],
				},
			),
			Tool(
				name="get_sales_by_channel",
				description="Analyze sales performance by sales channel with revenue breakdown",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
						"end_date": {"type": "string", "format": "date"},
					},
					"required": ["start_date", "end_date"],
				},
			),
			Tool(
				name="get_sales_forecast",
				description="Generate sales forecast based on historical data using linear regression",
				inputSchema={
					"type": "object",
					"properties": {
						"months_ahead": {"type": "integer", "default": 3},
						"category": {"type": "string"},
					},
				},
			),
			Tool(
				name="get_revenue_by_channel",
				description="Get revenue breakdown by sales channel",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
					},
				},
			),
			Tool(
				name="get_all_sales",
				description="Get all sales without filtering - simple test method",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_sales",
				description="Get sales with flexible filtering by any property (amount, date, category, etc.)",
				inputSchema={
					"type": "object",
					"properties": {
						"filters": {
							"type": "object",
							"description": "Filter by any sales property (amount, sale_date, category, product_name, etc.)",
							"additionalProperties": True,
							"examples": [
								{"amount": {"min": 100, "max": 500}},
								{"category": "Electronics"},
								{
									"sale_date": {
										"min": "2024-01-01",
										"max": "2024-12-31",
									}
								},
								{"product_name": {"like": "%laptop%"}},
								{"payment_status": "completed"},
							],
						},
						"order_by": {
							"type": "string",
							"description": "Field to order by (amount, sale_date, product_name, etc.)",
						},
						"limit": {
							"type": "integer",
							"description": "Maximum number of records to return",
						},
						"offset": {
							"type": "integer",
							"description": "Number of records to skip",
							"default": 0,
						},
					},
				},
			),
		]

	@staticmethod
	def get_customer_tools() -> list[Tool]:
		"""Get customer analytics tools."""
		return [
			Tool(
				name="get_top_customers",
				description="Get top customers ranked by total spending",
				inputSchema={
					"type": "object",
					"properties": {
						"limit": {"type": "integer", "default": 10},
					},
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
				name="get_customers_summary",
				description="Get overall customers summary statistics",
				inputSchema={"type": "object", "properties": {}},
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
				name="get_customer_purchase_history",
				description="Get detailed purchase history for a specific customer",
				inputSchema={
					"type": "object",
					"properties": {
						"customer_id": {
							"type": "integer",
							"description": "ID of the customer",
						},
						"limit": {
							"type": "integer",
							"default": 50,
							"description": "Maximum number of purchases to return",
						},
					},
					"required": ["customer_id"],
				},
			),
			Tool(
				name="get_customers",
				description="Get customers with flexible filtering by any property (name, email, type, credit_limit, etc.)",
				inputSchema={
					"type": "object",
					"properties": {
						"filters": {
							"type": "object",
							"description": "Filter by any customer property (customer_name, email, customer_type, credit_limit, etc.)",
							"additionalProperties": True,
							"examples": [
								{"customer_type": "retail"},
								{"credit_limit": {"min": 1000}},
								{"is_active": True},
								{"city": "New York"},
								{"customer_name": {"like": "%john%"}},
							],
						},
						"order_by": {
							"type": "string",
							"description": "Field to order by (customer_name, created_at, credit_limit, etc.)",
						},
						"limit": {
							"type": "integer",
							"description": "Maximum number of records to return",
						},
						"offset": {
							"type": "integer",
							"description": "Number of records to skip",
							"default": 0,
						},
					},
				},
			),
			Tool(
				name="get_customer_segmentation",
				description="Segment customers based on purchasing behavior (RFM analysis)",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_customer_lifetime_value",
				description="Calculate customer lifetime value and related metrics",
				inputSchema={
					"type": "object",
					"properties": {
						"customer_id": {"type": "integer"},
					},
				},
			),
		]

	@staticmethod
	def get_product_tools() -> list[Tool]:
		"""Get product analytics tools."""
		return [
			Tool(
				name="get_top_products",
				description="Get the top selling products ranked by sales amount",
				inputSchema={
					"type": "object",
					"properties": {
						"limit": {"type": "integer", "default": 10},
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
				name="get_products_summary",
				description="Get overall products summary statistics",
				inputSchema={"type": "object", "properties": {}},
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
				name="get_products",
				description="Get products with flexible filtering by any property (name, price, stock, category, etc.)",
				inputSchema={
					"type": "object",
					"properties": {
						"filters": {
							"type": "object",
							"description": "Filter by any product property (product_name, unit_price, stock_quantity, category_id, etc.)",
							"additionalProperties": True,
							"examples": [
								{"unit_price": {"min": 50, "max": 200}},
								{"category_id": 1},
								{"is_active": True},
								{"stock_quantity": {"min": 10}},
								{"product_name": {"like": "%laptop%"}},
							],
						},
						"order_by": {
							"type": "string",
							"description": "Field to order by (product_name, unit_price, stock_quantity, etc.)",
						},
						"limit": {
							"type": "integer",
							"description": "Maximum number of records to return",
						},
						"offset": {
							"type": "integer",
							"description": "Number of records to skip",
							"default": 0,
						},
					},
				},
			),
			Tool(
				name="get_categories",
				description="Get categories with flexible filtering by any property (name, parent, active status, etc.)",
				inputSchema={
					"type": "object",
					"properties": {
						"filters": {
							"type": "object",
							"description": "Filter by any category property (category_name, is_active, parent_category_id, etc.)",
							"additionalProperties": True,
							"examples": [
								{"is_active": True},
								{"parent_category_id": None},
								{"category_name": {"like": "%electronics%"}},
							],
						},
						"order_by": {
							"type": "string",
							"description": "Field to order by (category_name, created_at, etc.)",
						},
						"limit": {
							"type": "integer",
							"description": "Maximum number of records to return",
						},
						"offset": {
							"type": "integer",
							"description": "Number of records to skip",
							"default": 0,
						},
					},
				},
			),
			Tool(
				name="get_product_performance_analysis",
				description="Comprehensive product performance analysis with velocity and profit margins",
				inputSchema={
					"type": "object",
					"properties": {
						"product_id": {"type": "integer"},
					},
				},
			),
		]

	@staticmethod
	def get_invoice_tools() -> list[Tool]:
		"""Get invoice and financial tools."""
		return [
			Tool(
				name="get_pending_invoices",
				description="Get all pending/unpaid invoices",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_invoice_summary",
				description="Get invoice summary with optional date filter",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
					},
				},
			),
			Tool(
				name="get_invoices",
				description="Get invoices with flexible filtering by any property (amount, date, status, customer, etc.)",
				inputSchema={
					"type": "object",
					"properties": {
						"filters": {
							"type": "object",
							"description": "Filter by any invoice property (total_amount, invoice_date, status, customer_id, etc.)",
							"additionalProperties": True,
							"examples": [
								{"status": "paid"},
								{"total_amount": {"min": 1000}},
								{
									"invoice_date": {
										"min": "2024-01-01",
										"max": "2024-12-31",
									}
								},
								{"customer_id": 123},
								{"payment_method": "credit_card"},
							],
						},
						"order_by": {
							"type": "string",
							"description": "Field to order by (invoice_date, total_amount, status, etc.)",
						},
						"limit": {
							"type": "integer",
							"description": "Maximum number of records to return",
						},
						"offset": {
							"type": "integer",
							"description": "Number of records to skip",
							"default": 0,
						},
					},
				},
			),
			Tool(
				name="get_invoice_analysis",
				description="Comprehensive invoice analysis with financial metrics and overdue tracking",
				inputSchema={"type": "object", "properties": {}},
			),
		]

	@staticmethod
	def get_analytics_tools() -> list[Tool]:
		"""Get advanced analytics tools."""
		return [
			Tool(
				name="get_inventory_analysis",
				description="Comprehensive inventory analysis with reorder recommendations",
				inputSchema={
					"type": "object",
					"properties": {
						"include_inactive": {"type": "boolean", "default": False},
					},
				},
			),
			Tool(
				name="get_category_performance",
				description="Analyze performance by product category with revenue breakdown",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_revenue_analysis",
				description="Comprehensive revenue analysis with trends and growth rates",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
						"end_date": {"type": "string", "format": "date"},
						"group_by": {
							"type": "string",
							"enum": ["day", "week", "month", "quarter"],
							"default": "month",
						},
					},
					"required": ["start_date", "end_date"],
				},
			),
		]

	@staticmethod
	def get_discovery_tools() -> list[Tool]:
		"""Get tool discovery and metadata tools."""
		return [
			Tool(
				name="get_tool_groups",
				description="Get available tool groups and their associated tools",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_tool_categories",
				description="Get available tool categories and their associated tools",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_tool_namespaces",
				description="Get available tool namespaces and their original tool names",
				inputSchema={"type": "object", "properties": {}},
			),
			Tool(
				name="get_tool_metadata",
				description="Get comprehensive tool metadata including groups, categories, and namespaces",
				inputSchema={"type": "object", "properties": {}},
			),
		]

	@staticmethod
	def get_chart_tools() -> list[Tool]:
		"""Get chart generation and visualization tools."""
		return [
			Tool(
				name="create_sales_trend_chart",
				description="Create a sales trend chart showing revenue over time",
				inputSchema={
					"type": "object",
					"properties": {
						"period": {
							"type": "string",
							"enum": ["day", "week", "month", "year"],
							"default": "month",
						},
						"limit": {
							"type": "integer",
							"minimum": 1,
							"maximum": 100,
							"default": 12,
						},
						"chart_type": {
							"type": "string",
							"enum": ["line", "bar"],
							"default": "line",
						},
					},
				},
			),
			Tool(
				name="create_top_products_chart",
				description="Create a chart showing top products by revenue or quantity",
				inputSchema={
					"type": "object",
					"properties": {
						"limit": {
							"type": "integer",
							"minimum": 1,
							"maximum": 50,
							"default": 10,
						},
						"chart_type": {
							"type": "string",
							"enum": ["bar", "pie"],
							"default": "bar",
						},
						"metric": {
							"type": "string",
							"enum": ["revenue", "quantity"],
							"default": "revenue",
						},
					},
				},
			),
			Tool(
				name="create_sales_by_category_chart",
				description="Create a chart showing sales breakdown by product category",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {"type": "string", "format": "date"},
						"chart_type": {
							"type": "string",
							"enum": ["pie", "bar"],
							"default": "pie",
						},
					},
				},
			),
			Tool(
				name="create_customer_analysis_chart",
				description="Create a chart showing top customers by revenue",
				inputSchema={
					"type": "object",
					"properties": {
						"limit": {
							"type": "integer",
							"minimum": 1,
							"maximum": 50,
							"default": 10,
						},
						"chart_type": {
							"type": "string",
							"enum": ["bar", "pie"],
							"default": "bar",
						},
					},
				},
			),
			Tool(
				name="create_sales_comparison_chart",
				description="Create a chart comparing sales between two periods",
				inputSchema={
					"type": "object",
					"properties": {
						"period1_start": {"type": "string", "format": "date"},
						"period1_end": {"type": "string", "format": "date"},
						"period2_start": {"type": "string", "format": "date"},
						"period2_end": {"type": "string", "format": "date"},
						"chart_type": {
							"type": "string",
							"enum": ["bar"],
							"default": "bar",
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
				name="create_custom_query_chart",
				description="Create a chart from a custom SQL query",
				inputSchema={
					"type": "object",
					"properties": {
						"sql_query": {"type": "string"},
						"chart_type": {
							"type": "string",
							"enum": ["bar", "line", "pie"],
							"default": "bar",
						},
						"x_column": {"type": "string"},
						"y_column": {"type": "string"},
						"title": {"type": "string", "default": "Custom Chart"},
					},
					"required": ["sql_query"],
				},
			),
		]

	@staticmethod
	def get_file_tools() -> list[Tool]:
		"""Get file generation and export tools."""
		return [
			Tool(
				name="export_sales_to_csv",
				description="Export sales data to CSV format with optional date filtering",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {
							"type": "string",
							"format": "date",
							"description": "Start date for sales data (YYYY-MM-DD)",
						},
						"end_date": {
							"type": "string",
							"format": "date",
							"description": "End date for sales data (YYYY-MM-DD)",
						},
						"include_details": {
							"type": "boolean",
							"default": True,
							"description": "Include detailed customer and product information",
						},
					},
				},
			),
			Tool(
				name="export_customers_to_csv",
				description="Export customer data to CSV format with sales summary",
				inputSchema={
					"type": "object",
					"properties": {
						"customer_type": {
							"type": "string",
							"description": "Filter by customer type (individual, corporate, etc.)",
						},
						"include_sales_summary": {
							"type": "boolean",
							"default": True,
							"description": "Include sales summary for each customer",
						},
					},
				},
			),
			Tool(
				name="export_products_to_excel",
				description="Export product data to Excel format with multiple sheets",
				inputSchema={
					"type": "object",
					"properties": {
						"category": {
							"type": "string",
							"description": "Filter by product category",
						},
						"include_sales_data": {
							"type": "boolean",
							"default": True,
							"description": "Include sales performance data in separate sheet",
						},
					},
				},
			),
			Tool(
				name="export_sales_report_to_pdf",
				description="Generate comprehensive sales report in PDF format",
				inputSchema={
					"type": "object",
					"properties": {
						"start_date": {
							"type": "string",
							"format": "date",
							"description": "Start date for report period (YYYY-MM-DD)",
						},
						"end_date": {
							"type": "string",
							"format": "date",
							"description": "End date for report period (YYYY-MM-DD)",
						},
						"report_title": {
							"type": "string",
							"default": "Sales Report",
							"description": "Title for the PDF report",
						},
					},
				},
			),
			Tool(
				name="export_custom_query_to_excel",
				description="Export custom query results to Excel with multiple analysis sheets",
				inputSchema={
					"type": "object",
					"properties": {
						"query_type": {
							"type": "string",
							"enum": [
								"comprehensive_sales",
								"customer_analysis",
								"product_performance",
							],
							"description": "Type of analysis to export",
						},
						"filters": {
							"type": "object",
							"description": "Additional filters for the analysis",
							"properties": {
								"start_date": {"type": "string", "format": "date"},
								"end_date": {"type": "string", "format": "date"},
								"category": {"type": "string"},
							},
						},
						"export_format": {
							"type": "string",
							"enum": ["xlsx"],
							"default": "xlsx",
							"description": "Export format (currently only Excel supported)",
						},
					},
					"required": ["query_type"],
				},
			),
		]

	@classmethod
	def get_all_tools(cls) -> list[Tool]:
		"""Get all available tools."""
		return (
			cls.get_ai_insights_tools()
			+ cls.get_sales_tools()
			+ cls.get_customer_tools()
			+ cls.get_product_tools()
			+ cls.get_invoice_tools()
			+ cls.get_analytics_tools()
			+ cls.get_discovery_tools()
			+ cls.get_chart_tools()
			+ cls.get_file_tools()
		)

	@classmethod
	def get_tool_metadata(cls) -> dict[str, dict[str, str]]:
		"""Get tool metadata including groups, categories, and namespaces."""
		return {
			# AI Insights Tools
			"get_sales_analytics": {
				"group": "ai",
				"category": "insights",
				"namespace": "ai.sales_analytics",
			},
			"get_customer_insights": {
				"group": "ai",
				"category": "insights",
				"namespace": "ai.customer_insights",
			},
			"get_product_performance": {
				"group": "ai",
				"category": "insights",
				"namespace": "ai.product_performance",
			},
			"get_business_insights": {
				"group": "ai",
				"category": "insights",
				"namespace": "ai.business_insights",
			},
			"compare_periods": {
				"group": "ai",
				"category": "insights",
				"namespace": "ai.compare_periods",
			},
			# Sales Tools
			"get_sales_by_period": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.by_period",
			},
			"compare_sales_periods": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.compare_periods",
			},
			"get_sales_by_category": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.by_category",
			},
			"get_sales_summary": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.summary",
			},
			"get_sales_trends": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.trends",
			},
			"get_top_selling_products": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.top_products",
			},
			"get_sales_by_channel": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.by_channel",
			},
			"get_sales_forecast": {
				"group": "sales",
				"category": "forecasting",
				"namespace": "sales.forecast",
			},
			"get_revenue_by_channel": {
				"group": "sales",
				"category": "analytics",
				"namespace": "sales.revenue_by_channel",
			},
			"get_all_sales": {
				"group": "sales",
				"category": "data",
				"namespace": "sales.all",
			},
			"get_sales": {
				"group": "sales",
				"category": "data",
				"namespace": "sales.filtered",
			},
			# Customer Tools
			"get_top_customers": {
				"group": "customers",
				"category": "analytics",
				"namespace": "customers.top",
			},
			"get_customer_details": {
				"group": "customers",
				"category": "data",
				"namespace": "customers.details",
			},
			"get_customers_summary": {
				"group": "customers",
				"category": "analytics",
				"namespace": "customers.summary",
			},
			"search_customers": {
				"group": "customers",
				"category": "search",
				"namespace": "customers.search",
			},
			"get_customer_purchase_history": {
				"group": "customers",
				"category": "data",
				"namespace": "customers.purchase_history",
			},
			"get_customers": {
				"group": "customers",
				"category": "data",
				"namespace": "customers.filtered",
			},
			"get_customer_segmentation": {
				"group": "customers",
				"category": "analytics",
				"namespace": "customers.segmentation",
			},
			"get_customer_lifetime_value": {
				"group": "customers",
				"category": "analytics",
				"namespace": "customers.lifetime_value",
			},
			# Product Tools
			"get_top_products": {
				"group": "products",
				"category": "analytics",
				"namespace": "products.top",
			},
			"get_products_low_stock": {
				"group": "products",
				"category": "inventory",
				"namespace": "products.low_stock",
			},
			"get_products_summary": {
				"group": "products",
				"category": "analytics",
				"namespace": "products.summary",
			},
			"get_product_details": {
				"group": "products",
				"category": "data",
				"namespace": "products.details",
			},
			"search_products": {
				"group": "products",
				"category": "search",
				"namespace": "products.search",
			},
			"get_products": {
				"group": "products",
				"category": "data",
				"namespace": "products.filtered",
			},
			"get_categories": {
				"group": "products",
				"category": "data",
				"namespace": "products.categories",
			},
			"get_product_performance_analysis": {
				"group": "products",
				"category": "analytics",
				"namespace": "products.performance",
			},
			# Invoice Tools
			"get_pending_invoices": {
				"group": "invoices",
				"category": "financial",
				"namespace": "invoices.pending",
			},
			"get_invoice_summary": {
				"group": "invoices",
				"category": "analytics",
				"namespace": "invoices.summary",
			},
			"get_invoices": {
				"group": "invoices",
				"category": "data",
				"namespace": "invoices.filtered",
			},
			"get_invoice_analysis": {
				"group": "invoices",
				"category": "analytics",
				"namespace": "invoices.analysis",
			},
			# Analytics Tools
			"get_inventory_analysis": {
				"group": "analytics",
				"category": "inventory",
				"namespace": "analytics.inventory",
			},
			"get_category_performance": {
				"group": "analytics",
				"category": "performance",
				"namespace": "analytics.category_performance",
			},
			"get_revenue_analysis": {
				"group": "analytics",
				"category": "financial",
				"namespace": "analytics.revenue",
			},
			# Discovery Tools
			"get_tool_groups": {
				"group": "discovery",
				"category": "metadata",
				"namespace": "discovery.groups",
			},
			"get_tool_categories": {
				"group": "discovery",
				"category": "metadata",
				"namespace": "discovery.categories",
			},
			"get_tool_namespaces": {
				"group": "discovery",
				"category": "metadata",
				"namespace": "discovery.namespaces",
			},
			"get_tool_metadata": {
				"group": "discovery",
				"category": "metadata",
				"namespace": "discovery.metadata",
			},
			# Chart Tools
			"create_sales_trend_chart": {
				"group": "charts",
				"category": "visualization",
				"namespace": "charts.sales_trend",
			},
			"create_top_products_chart": {
				"group": "charts",
				"category": "visualization",
				"namespace": "charts.top_products",
			},
			"create_sales_by_category_chart": {
				"group": "charts",
				"category": "visualization",
				"namespace": "charts.sales_by_category",
			},
			"create_customer_analysis_chart": {
				"group": "charts",
				"category": "visualization",
				"namespace": "charts.customer_analysis",
			},
			"create_sales_comparison_chart": {
				"group": "charts",
				"category": "visualization",
				"namespace": "charts.sales_comparison",
			},
			"create_custom_query_chart": {
				"group": "charts",
				"category": "visualization",
				"namespace": "charts.custom_query",
			},
			# File Export Tools
			"export_sales_to_csv": {
				"group": "files",
				"category": "export",
				"namespace": "files.sales_csv",
			},
			"export_customers_to_csv": {
				"group": "files",
				"category": "export",
				"namespace": "files.customers_csv",
			},
			"export_products_to_excel": {
				"group": "files",
				"category": "export",
				"namespace": "files.products_excel",
			},
			"export_sales_report_to_pdf": {
				"group": "files",
				"category": "export",
				"namespace": "files.sales_pdf",
			},
			"export_custom_query_to_excel": {
				"group": "files",
				"category": "export",
				"namespace": "files.custom_excel",
			},
		}

	@classmethod
	def get_namespace_aliases(cls) -> dict[str, str]:
		"""Get namespace aliases for backward compatibility."""
		metadata = cls.get_tool_metadata()
		aliases = {}

		for tool_name, meta in metadata.items():
			namespace = meta["namespace"]
			aliases[namespace] = tool_name

		return aliases

	@classmethod
	def get_tools_by_group(cls, group: str) -> list[Tool]:
		"""Get tools filtered by group."""
		all_tools = cls.get_all_tools()
		metadata = cls.get_tool_metadata()

		return [
			tool
			for tool in all_tools
			if metadata.get(tool.name, {}).get("group") == group
		]

	@classmethod
	def get_tools_by_category(cls, category: str) -> list[Tool]:
		"""Get tools filtered by category."""
		all_tools = cls.get_all_tools()
		metadata = cls.get_tool_metadata()

		return [
			tool
			for tool in all_tools
			if metadata.get(tool.name, {}).get("category") == category
		]

	@classmethod
	def get_tools_by_namespace(cls, namespace: str) -> list[Tool]:
		"""Get tools filtered by namespace."""
		all_tools = cls.get_all_tools()
		metadata = cls.get_tool_metadata()

		return [
			tool
			for tool in all_tools
			if metadata.get(tool.name, {}).get("namespace") == namespace
		]

	@classmethod
	def get_available_groups(cls) -> list[str]:
		"""Get list of available tool groups."""
		metadata = cls.get_tool_metadata()
		return sorted({meta["group"] for meta in metadata.values()})

	@classmethod
	def get_available_categories(cls) -> list[str]:
		"""Get list of available tool categories."""
		metadata = cls.get_tool_metadata()
		return sorted({meta["category"] for meta in metadata.values()})

	@classmethod
	def get_available_namespaces(cls) -> list[str]:
		"""Get list of available tool namespaces."""
		metadata = cls.get_tool_metadata()
		return sorted({meta["namespace"] for meta in metadata.values()})
