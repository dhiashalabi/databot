from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from .analytics_tools import AnalyticsTools
from .base_tools import BaseTools
from .chart_tools import ChartTools
from .customer_tools import CustomerTools
from .file_tools import FileTools
from .invoice_tools import InvoiceTools
from .product_tools import ProductTools
from .sales_tools import SalesTools


class MCPTools(BaseTools):
	"""Main MCP tools class that orchestrates all specialized tool modules."""

	def __init__(self, db: AsyncSession):
		"""Initialize with database session and all tool modules."""
		super().__init__(db)

		self.sales = SalesTools(db)
		self.customers = CustomerTools(db)
		self.products = ProductTools(db)
		self.invoices = InvoiceTools(db)
		self.analytics = AnalyticsTools(db)
		self.charts = ChartTools(db)
		self.files = FileTools(db)

	async def get_sales_by_period(
		self, start_date: str, end_date: str | None = None
	) -> list:
		"""Get sales data for a specific period."""
		return await self.sales.get_sales_by_period(start_date, end_date)

	async def compare_sales_periods(
		self, period1_start: str, period1_end: str, period2_start: str, period2_end: str
	) -> dict[str, Any]:
		"""Compare sales between two periods."""
		return await self.sales.compare_sales_periods(
			period1_start, period1_end, period2_start, period2_end
		)

	async def get_sales_by_category(self, start_date: str | None = None) -> list:
		"""Get sales grouped by category."""
		return await self.sales.get_sales_by_category(start_date)

	async def get_sales_summary(self) -> dict[str, Any]:
		"""Get overall sales summary."""
		return await self.sales.get_sales_summary()

	async def get_all_sales(self) -> dict[str, Any]:
		"""Get all sales without any filtering - simple test method."""
		return await self.sales.get_all_sales()

	async def get_sales(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get sales with flexible filtering by any property."""
		return await self.sales.get_sales(filters, order_by, limit, offset)

	async def get_top_customers(self, limit: int = 10) -> list:
		"""Get top customers by total purchase amount."""
		return await self.customers.get_top_customers(limit)

	async def get_customer_details(self, customer_name: str) -> dict | None:
		"""Get detailed information about a specific customer."""
		return await self.customers.get_customer_details(customer_name)

	async def get_customers_summary(self) -> dict[str, Any]:
		"""Get overall customers summary."""
		return await self.customers.get_customers_summary()

	async def search_customers(
		self,
		search_term: str | None = None,
		customer_type: str | None = None,
		limit: int = 20,
	) -> list[dict[str, Any]]:
		"""Search customers by various criteria."""
		return await self.customers.search_customers(search_term, customer_type, limit)

	async def get_customer_purchase_history(
		self, customer_id: int, limit: int = 50
	) -> dict[str, Any]:
		"""Get detailed purchase history for a customer."""
		return await self.customers.get_customer_purchase_history(customer_id, limit)

	async def get_customers(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get customers with flexible filtering by any property."""
		return await self.customers.get_customers(filters, order_by, limit, offset)

	async def get_top_products(self, limit: int = 10) -> list:
		"""Get top selling products by quantity and revenue."""
		return await self.products.get_top_products(limit)

	async def get_products_low_stock(self, threshold: int = 20) -> list:
		"""Get products with low stock levels."""
		return await self.products.get_products_low_stock(threshold)

	async def get_products_summary(self) -> dict[str, Any]:
		"""Get overall products summary."""
		return await self.products.get_products_summary()

	async def get_product_details(
		self, product_id: int | None = None, product_name: str | None = None
	) -> dict[str, Any] | None:
		"""Get detailed information about a specific product."""
		return await self.products.get_product_details(product_id, product_name)

	async def search_products(
		self,
		search_term: str | None = None,
		category: str | None = None,
		low_stock_only: bool = False,
		limit: int = 20,
	) -> list[dict[str, Any]]:
		"""Search products by various criteria."""
		return await self.products.search_products(
			search_term, category, low_stock_only, limit
		)

	async def get_products(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get products with flexible filtering by any property."""
		return await self.products.get_products(filters, order_by, limit, offset)

	async def get_categories(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get categories with flexible filtering by any property."""
		return await self.products.get_categories(filters, order_by, limit, offset)

	async def get_pending_invoices(self) -> list:
		"""Get all pending invoices."""
		return await self.invoices.get_pending_invoices()

	async def get_invoice_summary(
		self, start_date: str | None = None
	) -> dict[str, Any]:
		"""Get invoice summary with optional date filter."""
		return await self.invoices.get_invoice_summary(start_date)

	async def get_revenue_by_channel(self, start_date: str | None = None) -> list:
		"""Get revenue breakdown by sales channel."""
		return await self.sales.get_revenue_by_channel(start_date)

	async def get_invoices(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get invoices with flexible filtering by any property."""
		return await self.invoices.get_invoices(filters, order_by, limit, offset)

	async def get_sales_trends(
		self,
		start_date: str,
		end_date: str,
		group_by: str = "day",
		category: str | None = None,
	) -> dict[str, Any]:
		"""Get sales trends over time with detailed analysis."""
		return await self.sales.get_sales_trends(
			start_date, end_date, group_by, category
		)

	async def get_top_selling_products(
		self,
		start_date: str,
		end_date: str,
		limit: int = 10,
		category: str | None = None,
	) -> dict[str, Any]:
		"""Get top selling products by revenue and quantity."""
		return await self.sales.get_top_selling_products(
			start_date, end_date, limit, category
		)

	async def get_sales_by_channel(
		self, start_date: str, end_date: str
	) -> dict[str, Any]:
		"""Analyze sales performance by sales channel."""
		return await self.sales.get_sales_by_channel(start_date, end_date)

	async def get_sales_forecast(
		self, periods: int = 6, period_type: str = "month"
	) -> dict[str, Any]:
		"""Generate sales forecast using simple linear regression."""
		return await self.analytics.get_sales_forecast(periods, period_type)

	async def get_customer_segmentation(self) -> dict[str, Any]:
		"""Perform RFM analysis for customer segmentation."""
		return await self.analytics.get_customer_segmentation()

	async def get_customer_lifetime_value(
		self, customer_id: int | None = None
	) -> dict[str, Any]:
		"""Calculate customer lifetime value."""
		return await self.analytics.get_customer_lifetime_value(customer_id)

	async def get_product_performance_analysis(
		self, product_id: int | None = None
	) -> dict[str, Any]:
		"""Analyze product performance metrics."""
		return await self.analytics.get_product_performance_analysis(product_id)

	async def get_inventory_analysis(self) -> dict[str, Any]:
		"""Analyze inventory levels and turnover."""
		return await self.analytics.get_inventory_analysis()

	async def get_category_performance(self) -> dict[str, Any]:
		"""Analyze performance by product category."""
		return await self.analytics.get_category_performance()

	async def get_invoice_analysis(self) -> dict[str, Any]:
		"""Analyze invoice patterns and payment behavior."""
		return await self.analytics.get_invoice_analysis()

	async def get_revenue_analysis(
		self, start_date: str | None = None, end_date: str | None = None
	) -> dict[str, Any]:
		"""Comprehensive revenue analysis."""
		return await self.analytics.get_revenue_analysis(start_date, end_date)

	async def create_sales_trend_chart(
		self, period: str = "month", limit: int = 12, chart_type: str = "line"
	) -> dict[str, Any]:
		"""Create a sales trend chart showing revenue over time."""
		return await self.charts.create_sales_trend_chart(period, limit, chart_type)

	async def create_sales_by_category_chart(
		self, start_date: str | None = None, chart_type: str = "pie"
	) -> dict[str, Any]:
		"""Create a sales by category chart."""
		return await self.charts.create_sales_by_category_chart(start_date, chart_type)

	async def create_top_products_chart(
		self, limit: int = 10, chart_type: str = "bar", metric: str = "revenue"
	) -> dict[str, Any]:
		"""Create a chart showing top products by revenue or quantity."""
		return await self.charts.create_top_products_chart(limit, chart_type, metric)

	async def create_customer_analysis_chart(
		self, limit: int = 10, chart_type: str = "bar"
	) -> dict[str, Any]:
		"""Create a chart showing top customers by revenue."""
		return await self.charts.create_customer_analysis_chart(limit, chart_type)

	async def create_sales_comparison_chart(
		self,
		period1_start: str,
		period1_end: str,
		period2_start: str,
		period2_end: str,
		chart_type: str = "bar",
	) -> dict[str, Any]:
		"""Create a chart comparing sales between two periods."""
		return await self.charts.create_sales_comparison_chart(
			period1_start, period1_end, period2_start, period2_end, chart_type
		)

	async def create_custom_query_chart(
		self,
		sql_query: str,
		chart_type: str = "bar",
		x_column: str | None = None,
		y_column: str | None = None,
		title: str = "Custom Chart",
	) -> dict[str, Any]:
		"""Create a chart from a custom SQL query."""
		return await self.charts.create_custom_query_chart(
			sql_query, chart_type, x_column, y_column, title
		)

	async def export_sales_to_csv(
		self,
		start_date: str | None = None,
		end_date: str | None = None,
		include_details: bool = True,
	) -> dict[str, Any]:
		"""Export sales data to CSV format."""
		return await self.files.export_sales_to_csv(
			start_date, end_date, include_details
		)

	async def export_customers_to_csv(
		self, customer_type: str | None = None, include_sales_summary: bool = True
	) -> dict[str, Any]:
		"""Export customer data to CSV format."""
		return await self.files.export_customers_to_csv(
			customer_type, include_sales_summary
		)

	async def export_products_to_excel(
		self, category: str | None = None, include_sales_data: bool = True
	) -> dict[str, Any]:
		"""Export product data to Excel format."""
		return await self.files.export_products_to_excel(category, include_sales_data)

	async def export_sales_report_to_pdf(
		self,
		start_date: str | None = None,
		end_date: str | None = None,
		report_title: str = "Sales Report",
	) -> dict[str, Any]:
		"""Export sales report to PDF format."""
		return await self.files.export_sales_report_to_pdf(
			start_date, end_date, report_title
		)

	async def export_custom_query_to_excel(
		self,
		query_type: str,
		filters: dict[str, Any] | None = None,
		export_format: str = "xlsx",
	) -> dict[str, Any]:
		"""Export custom query results to Excel format."""
		return await self.files.export_custom_query_to_excel(
			query_type, filters, export_format
		)

	async def export_customers_to_pdf(
		self,
		customer_type: str | None = None,
		limit: int | None = None,
		report_title: str = "Customer Report",
		include_sales_summary: bool = True,
	) -> dict[str, Any]:
		"""Export customers data to PDF format."""
		return await self.files.export_customers_to_pdf(
			customer_type, limit, report_title, include_sales_summary
		)

	async def export_top_customers_to_pdf(
		self,
		limit: int = 10,
		metric: str = "revenue",
		report_title: str | None = None,
	) -> dict[str, Any]:
		"""Export top customers to PDF format based on revenue or order count."""
		return await self.files.export_top_customers_to_pdf(limit, metric, report_title)

	async def export_products_to_pdf(
		self,
		category: str | None = None,
		limit: int | None = None,
		report_title: str = "Products Report",
		include_sales_data: bool = True,
	) -> dict[str, Any]:
		"""Export products data to PDF format."""
		return await self.files.export_products_to_pdf(
			category, limit, report_title, include_sales_data
		)
