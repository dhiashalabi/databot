"""Chart generation tools for MCP server with file-based storage."""

from pathlib import Path
from typing import Any
import uuid

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from sqlalchemy import func, select, text

from src.models.sales import Sale
from src.queries.sales_queries import SalesQueryBuilder

from .base_tools import BaseTools

matplotlib.use("Agg")


class ChartTools(BaseTools):
	"""Chart generation and visualization tools with file-based storage."""

	def __init__(self, db):
		"""Initialize chart tools with database session."""
		super().__init__(db)
		plt.style.use("default")
		self.charts_dir = Path("static/charts")
		self.charts_dir.mkdir(parents=True, exist_ok=True)

	def _save_chart_to_file(self, fig) -> str:
		"""Save matplotlib figure to file and return URL."""
		chart_id = str(uuid.uuid4())
		filename = f"chart_{chart_id}.png"
		file_path = self.charts_dir / filename

		fig.savefig(
			file_path,
			format="png",
			dpi=150,
			bbox_inches="tight",
			facecolor="white",
			edgecolor="none",
		)
		plt.close(fig)

		return f"/static/charts/{filename}"

	async def create_sales_trend_chart(
		self, period: str = "month", limit: int = 12, chart_type: str = "line"
	) -> dict[str, Any]:
		"""Create a sales trend chart showing revenue over time."""
		try:
			if period == "day":
				title = f"Sales Revenue Trend by Day (Last {limit} Days)"
				x_label = "Date"
			elif period == "week":
				title = f"Sales Revenue Trend by Week (Last {limit} Weeks)"
				x_label = "Week"
			elif period == "month":
				title = f"Sales Revenue Trend by Month (Last {limit} Months)"
				x_label = "Month"
			else:
				title = f"Sales Revenue Trend by Year (Last {limit} Years)"
				x_label = "Year"

			query = SalesQueryBuilder.build_sales_trends_query(
				period=period, limit=limit
			)
			result_rows = await self.db.execute(query)
			data = result_rows.fetchall()

			if not data:
				return {
					"error": "No sales data found for the specified period",
					"chart_url": None,
					"chart_data": [],
				}

			result = []
			for row in reversed(data):
				result.append(
					{
						"period": str(row.period),
						"total_revenue": float(row.total_revenue)
						if row.total_revenue
						else 0.0,
						"sales_count": int(row.sales_count),
						"avg_sale": float(row.avg_sale) if row.avg_sale else 0.0,
					}
				)

			total_revenue = sum(item["total_revenue"] for item in result)
			avg_revenue = total_revenue / len(result) if result else 0

			fig, ax = plt.subplots(figsize=(12, 6))

			periods = [item["period"][:10] for item in result]
			revenues = [item["total_revenue"] for item in result]

			if chart_type == "bar":
				ax.bar(periods, revenues, color="#2E86AB", alpha=0.8)
			else:
				ax.plot(periods, revenues, marker="o", linewidth=2, color="#2E86AB")

			ax.set_title(title, fontsize=16, fontweight="bold")
			ax.set_xlabel(x_label)
			ax.set_ylabel("Revenue ($)")
			ax.grid(True, alpha=0.3)

			ax.yaxis.set_major_formatter(
				ticker.FuncFormatter(lambda x, p: f"${x:,.0f}")
			)

			plt.xticks(rotation=45)
			plt.tight_layout()

			chart_url = self._save_chart_to_file(fig)

			return {
				"chart_url": chart_url,
				"chart_data": result,
				"metadata": {
					"title": title,
					"x_label": x_label,
					"y_label": "Revenue ($)",
					"chart_type": chart_type,
					"total_revenue": total_revenue,
					"avg_revenue": avg_revenue,
					"period_count": len(result),
				},
			}

		except Exception as e:
			return {
				"error": f"Failed to create sales trend chart: {e}",
				"chart_url": None,
				"chart_data": [],
			}

	async def create_sales_by_category_chart(
		self, start_date: str | None = None, chart_type: str = "pie"
	) -> dict[str, Any]:
		"""Create a sales by category chart."""
		try:
			query = SalesQueryBuilder.build_sales_by_category_query(start_date)
			result_rows = await self.db.execute(query)
			data = result_rows.fetchall()

			if not data:
				return {
					"error": "No sales data found by category",
					"chart_url": None,
					"chart_data": [],
				}

			result = []
			for row in data:
				result.append(
					{
						"category": row.category or "Unknown",
						"total_amount": float(row.total_amount)
						if row.total_amount
						else 0.0,
						"sales_count": int(row.sales_count),
						"avg_amount": float(row.avg_amount) if row.avg_amount else 0.0,
					}
				)

			fig, ax = plt.subplots(figsize=(10, 6))

			categories = [item["category"] for item in result]
			amounts = [item["total_amount"] for item in result]

			if chart_type == "bar":
				ax.bar(categories, amounts, color="#2E86AB", alpha=0.8)
				ax.set_ylabel("Revenue ($)")
				ax.set_xlabel("Category")
				ax.tick_params(axis="x", rotation=45)
			else:
				ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)

			ax.set_title("Sales by Category")
			plt.tight_layout()

			chart_url = self._save_chart_to_file(fig)

			return {
				"chart_url": chart_url,
				"chart_data": result,
				"metadata": {
					"title": "Sales by Category",
					"chart_type": chart_type,
					"total_categories": len(result),
					"total_revenue": sum(item["total_amount"] for item in result),
				},
			}

		except Exception as e:
			return {
				"error": f"Failed to create sales by category chart: {e}",
				"chart_url": None,
				"chart_data": [],
			}

	async def create_top_products_chart(
		self, limit: int = 10, chart_type: str = "bar", metric: str = "revenue"
	) -> dict[str, Any]:
		"""Create a chart showing top products by revenue or quantity."""
		try:
			if metric == "quantity":
				metric_col = func.sum(Sale.quantity)
				metric_label = "Quantity Sold"
				title = f"Top {limit} Products by Quantity Sold"
			else:
				metric_col = func.sum(Sale.amount)
				metric_label = "Revenue ($)"
				title = f"Top {limit} Products by Revenue"

			query = (
				select(
					Sale.product_name,
					metric_col.label("metric_value"),
					func.count(Sale.id).label("sales_count"),
				)
				.group_by(Sale.product_name)
				.order_by(metric_col.desc())
				.limit(limit)
			)

			result_rows = await self.db.execute(query)
			data = result_rows.fetchall()

			if not data:
				return {
					"error": "No product data found",
					"chart_url": None,
					"chart_data": [],
				}

			result = []
			for row in data:
				result.append(
					{
						"product_name": row.product_name,
						"metric_value": float(row.metric_value)
						if row.metric_value
						else 0.0,
						"sales_count": int(row.sales_count),
					}
				)

			fig, ax = plt.subplots(figsize=(12, 8))

			products = [item["product_name"] for item in result]
			values = [item["metric_value"] for item in result]

			if chart_type == "pie":
				ax.pie(values, labels=products, autopct="%1.1f%%", startangle=90)
				ax.set_title(title)
			else:
				ax.barh(products, values, color="#2E86AB", alpha=0.8)
				ax.set_xlabel(metric_label)
				ax.set_title(title)
				if metric == "revenue":
					ax.xaxis.set_major_formatter(
						ticker.FuncFormatter(lambda x, p: f"${x:,.0f}")
					)

			plt.tight_layout()

			chart_url = self._save_chart_to_file(fig)

			return {
				"chart_url": chart_url,
				"chart_data": result,
				"metadata": {
					"title": title,
					"metric": metric,
					"metric_label": metric_label,
					"chart_type": chart_type,
					"product_count": len(result),
				},
			}

		except Exception as e:
			return {
				"error": f"Failed to create top products chart: {e}",
				"chart_url": None,
				"chart_data": [],
			}

	async def create_customer_analysis_chart(
		self, limit: int = 10, analysis_type: str = "revenue", chart_type: str = "bar"
	) -> dict[str, Any]:
		"""Create a customer analysis chart showing top customers by revenue or frequency."""
		try:
			if analysis_type == "frequency":
				metric_col = func.count(Sale.id)
				metric_label = "Number of Purchases"
				title = f"Top {limit} Customers by Purchase Frequency"
			else:
				metric_col = func.sum(Sale.amount)
				metric_label = "Total Revenue ($)"
				title = f"Top {limit} Customers by Revenue"

			query = (
				select(
					Sale.customer_id,
					metric_col.label("metric_value"),
					func.sum(Sale.amount).label("total_revenue"),
					func.count(Sale.id).label("purchase_count"),
					func.avg(Sale.amount).label("avg_order_value"),
				)
				.group_by(Sale.customer_id)
				.order_by(metric_col.desc())
				.limit(limit)
			)

			result_rows = await self.db.execute(query)
			data = result_rows.fetchall()

			if not data:
				return {
					"error": "No customer data found",
					"chart_url": None,
					"chart_data": [],
				}

			result = []
			for row in data:
				result.append(
					{
						"customer_id": row.customer_id,
						"metric_value": float(row.metric_value)
						if row.metric_value
						else 0.0,
						"total_revenue": float(row.total_revenue)
						if row.total_revenue
						else 0.0,
						"purchase_count": int(row.purchase_count),
						"avg_order_value": float(row.avg_order_value)
						if row.avg_order_value
						else 0.0,
					}
				)

			fig, ax = plt.subplots(figsize=(12, 8))

			customers = [f"Customer {item['customer_id']}" for item in result]
			values = [item["metric_value"] for item in result]

			if chart_type == "pie":
				ax.pie(values, labels=customers, autopct="%1.1f%%", startangle=90)
			else:
				ax.barh(customers, values, color="#2E86AB", alpha=0.8)
				ax.set_xlabel(metric_label)
				if analysis_type == "revenue":
					ax.xaxis.set_major_formatter(
						ticker.FuncFormatter(lambda x, p: f"${x:,.0f}")
					)

			ax.set_title(title)
			plt.tight_layout()

			chart_url = self._save_chart_to_file(fig)

			return {
				"chart_url": chart_url,
				"chart_data": result,
				"metadata": {
					"title": title,
					"analysis_type": analysis_type,
					"metric_label": metric_label,
					"chart_type": chart_type,
					"customer_count": len(result),
				},
			}

		except Exception as e:
			return {
				"error": f"Failed to create customer analysis chart: {e}",
				"chart_url": None,
				"chart_data": [],
			}

	async def create_sales_comparison_chart(
		self,
		period1_start: str,
		period1_end: str,
		period2_start: str,
		period2_end: str,
		chart_type: str = "bar",
	) -> dict[str, Any]:
		"""Create a chart comparing sales between two periods."""
		try:
			from datetime import datetime

			p1_start = datetime.fromisoformat(period1_start)
			p1_end = datetime.fromisoformat(period1_end)
			p2_start = datetime.fromisoformat(period2_start)
			p2_end = datetime.fromisoformat(period2_end)

			period1_query = (
				select(
					func.sum(Sale.amount).label("total_revenue"),
					func.count(Sale.id).label("sales_count"),
					func.avg(Sale.amount).label("avg_order_value"),
				)
				.where(Sale.sale_date >= p1_start)
				.where(Sale.sale_date <= p1_end)
			)

			period2_query = (
				select(
					func.sum(Sale.amount).label("total_revenue"),
					func.count(Sale.id).label("sales_count"),
					func.avg(Sale.amount).label("avg_order_value"),
				)
				.where(Sale.sale_date >= p2_start)
				.where(Sale.sale_date <= p2_end)
			)

			period1_result = await self.db.execute(period1_query)
			period1_data = period1_result.fetchone()

			period2_result = await self.db.execute(period2_query)
			period2_data = period2_result.fetchone()

			if not period1_data and not period2_data:
				return {
					"error": "No data found for either period",
					"chart_url": None,
					"chart_data": [],
				}

			metrics = ["Total Revenue", "Sales Count", "Avg Order Value"]
			period1_values = [
				float(period1_data.total_revenue)
				if period1_data and period1_data.total_revenue
				else 0,
				int(period1_data.sales_count)
				if period1_data and period1_data.sales_count
				else 0,
				float(period1_data.avg_order_value)
				if period1_data and period1_data.avg_order_value
				else 0,
			]
			period2_values = [
				float(period2_data.total_revenue)
				if period2_data and period2_data.total_revenue
				else 0,
				int(period2_data.sales_count)
				if period2_data and period2_data.sales_count
				else 0,
				float(period2_data.avg_order_value)
				if period2_data and period2_data.avg_order_value
				else 0,
			]

			fig, ax = plt.subplots(figsize=(12, 6))

			x = range(len(metrics))
			width = 0.35

			ax.bar(
				[i - width / 2 for i in x],
				period1_values,
				width,
				label=f"Period 1 ({period1_start[:10]})",
				alpha=0.8,
			)
			ax.bar(
				[i + width / 2 for i in x],
				period2_values,
				width,
				label=f"Period 2 ({period2_start[:10]})",
				alpha=0.8,
			)

			ax.set_xlabel("Metrics")
			ax.set_ylabel("Values")
			ax.set_title("Sales Comparison Between Periods")
			ax.set_xticks(x)
			ax.set_xticklabels(metrics)
			ax.legend()

			plt.tight_layout()

			chart_url = self._save_chart_to_file(fig)

			return {
				"chart_url": chart_url,
				"chart_data": {
					"period1": {
						"start": period1_start,
						"end": period1_end,
						"total_revenue": period1_values[0],
						"sales_count": period1_values[1],
						"avg_order_value": period1_values[2],
					},
					"period2": {
						"start": period2_start,
						"end": period2_end,
						"total_revenue": period2_values[0],
						"sales_count": period2_values[1],
						"avg_order_value": period2_values[2],
					},
				},
				"metadata": {
					"title": "Sales Comparison Between Periods",
					"chart_type": chart_type,
				},
			}

		except Exception as e:
			return {
				"error": f"Failed to create sales comparison chart: {e}",
				"chart_url": None,
				"chart_data": [],
			}

	async def create_custom_query_chart(
		self,
		sql_query: str,
		chart_type: str = "bar",
		x_column: str | None = None,
		y_column: str | None = None,
		title: str = "Custom Chart",
	) -> dict[str, Any]:
		"""Create a chart from a custom SQL query."""
		try:
			result = await self.db.execute(text(sql_query))
			data = result.fetchall()

			if not data:
				return {
					"error": "No data returned from query",
					"chart_url": None,
					"chart_data": [],
				}

			df = pd.DataFrame(data)

			if df.empty:
				return {
					"error": "Query returned empty results",
					"chart_url": None,
					"chart_data": [],
				}

			if not x_column and len(df.columns) > 0:
				x_column = df.columns[0]
			if not y_column and len(df.columns) > 1:
				y_column = df.columns[1]

			if not x_column or not y_column:
				return {
					"error": "Could not determine x and y columns",
					"chart_url": None,
					"chart_data": [],
				}

			fig, ax = plt.subplots(figsize=(12, 6))

			if chart_type == "pie":
				ax.pie(
					df[y_column],
					labels=df[x_column].astype(str),
					autopct="%1.1f%%",
					startangle=90,
				)
			elif chart_type == "line":
				ax.plot(df[x_column], df[y_column], marker="o")
				ax.set_xlabel(x_column)
				ax.set_ylabel(y_column)
			else:
				ax.bar(df[x_column].astype(str), df[y_column])
				ax.set_xlabel(x_column)
				ax.set_ylabel(y_column)

			ax.set_title(title)
			plt.tight_layout()

			chart_url = self._save_chart_to_file(fig)

			return {
				"chart_url": chart_url,
				"chart_data": df.to_dict("records"),
				"metadata": {
					"title": title,
					"chart_type": chart_type,
					"x_column": x_column,
					"y_column": y_column,
					"row_count": len(df),
				},
			}

		except Exception as e:
			return {
				"error": f"Failed to create custom query chart: {e}",
				"chart_url": None,
				"chart_data": [],
			}
