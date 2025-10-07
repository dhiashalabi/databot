"""Sales-related tools for MCP server."""

from typing import Any

from sqlalchemy import and_, desc, func, select

from src.models.sales import Sale
from src.queries import SalesQueryBuilder

from .base_tools import BaseTools


class SalesTools(BaseTools):
	"""Tools for sales data analysis and querying."""

	async def get_sales_by_period(
		self, start_date: str, end_date: str | None = None
	) -> list:
		"""Get sales data for a specific period."""
		try:
			await self.db.rollback()

			query = SalesQueryBuilder.build_sales_by_period_query(start_date, end_date)
			result = await self.db.execute(query)
			sales = result.scalars().all()
			return [self._format_sale_data(sale) for sale in sales]
		except Exception:
			return []

	async def compare_sales_periods(
		self, period1_start: str, period1_end: str, period2_start: str, period2_end: str
	) -> dict[str, Any]:
		"""Compare sales between two periods."""
		try:
			period1_sales = await self.get_sales_by_period(period1_start, period1_end)
			period2_sales = await self.get_sales_by_period(period2_start, period2_end)

			period1_total = sum(sale["amount"] for sale in period1_sales)
			period2_total = sum(sale["amount"] for sale in period2_sales)
			period1_count = len(period1_sales)
			period2_count = len(period2_sales)

			growth_rate = (
				((period2_total - period1_total) / period1_total * 100)
				if period1_total > 0
				else 0
			)

			return {
				"period1": {
					"start_date": period1_start,
					"end_date": period1_end,
					"total_sales": period1_total,
					"sales_count": period1_count,
				},
				"period2": {
					"start_date": period2_start,
					"end_date": period2_end,
					"total_sales": period2_total,
					"sales_count": period2_count,
				},
				"comparison": {
					"growth_rate": round(growth_rate, 2),
					"sales_difference": period2_total - period1_total,
					"count_difference": period2_count - period1_count,
				},
			}
		except Exception as e:
			return {"error": f"Error comparing periods: {str(e)}"}

	async def get_sales_by_category(self, start_date: str | None = None) -> list:
		"""Get sales grouped by category."""
		try:
			await self.db.rollback()

			query = SalesQueryBuilder.build_sales_by_category_query(start_date)
			result = await self.db.execute(query)
			categories = result.fetchall()

			return [
				{
					"category": cat.category,
					"total_amount": float(cat.total_amount),
					"sales_count": cat.sales_count,
					"avg_amount": float(cat.avg_amount),
				}
				for cat in categories
			]
		except Exception:
			return []

	async def get_sales_summary(self) -> dict[str, Any]:
		"""Get overall sales summary."""
		try:
			await self.db.rollback()

			query = select(
				func.count(Sale.id).label("total_sales"),
				func.sum(Sale.amount).label("total_revenue"),
				func.avg(Sale.amount).label("avg_sale"),
				func.min(Sale.sale_date).label("first_sale"),
				func.max(Sale.sale_date).label("last_sale"),
			)

			result = await self.db.execute(query)
			summary = result.fetchone()

			return {
				"total_sales": summary.total_sales,
				"total_revenue": float(summary.total_revenue or 0),
				"avg_sale": float(summary.avg_sale or 0),
				"first_sale": summary.first_sale.isoformat()
				if summary.first_sale
				else None,
				"last_sale": summary.last_sale.isoformat()
				if summary.last_sale
				else None,
			}
		except Exception as e:
			return {"error": f"Error getting sales summary: {str(e)}"}

	async def get_all_sales(self) -> dict[str, Any]:
		"""Get all sales without any filtering - simple test method."""
		try:
			query = SalesQueryBuilder.build_sales_query()
			result = await self.db.execute(query)
			sales = result.scalars().all()

			sales_data = [self._format_sale_data(sale) for sale in sales]

			return {
				"sales": sales_data,
				"total_count": len(sales_data),
				"total_amount": sum(float(sale.amount) for sale in sales),
			}
		except Exception as e:
			return {
				"error": f"Error getting all sales: {str(e)}",
				"error_type": type(e).__name__,
				"sales": [],
				"total_count": 0,
				"total_amount": 0,
			}

	async def get_sales(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get sales with flexible filtering by any property."""
		try:
			query = SalesQueryBuilder.build_sales_query(filters, order_by)
			query = SalesQueryBuilder.apply_pagination(query, limit, offset)

			result = await self.db.execute(query)
			sales = result.scalars().all()

			count_query = SalesQueryBuilder.build_sales_count_query(filters)
			count_result = await self.db.execute(count_query)
			total_count = count_result.scalar()

			sales_data = [self._format_sale_data(sale) for sale in sales]

			return {
				"sales": sales_data,
				"summary": {
					"total_count": total_count,
					"returned_count": len(sales_data),
					"total_amount": sum(float(sale.amount) for sale in sales),
					"total_quantity": sum(sale.quantity for sale in sales),
				},
			}
		except Exception as e:
			return {
				"error": f"Error querying sales: {str(e)}",
				"error_type": type(e).__name__,
				"sales": [],
				"summary": {
					"total_count": 0,
					"returned_count": 0,
					"total_amount": 0,
					"total_quantity": 0,
				},
			}

	async def get_revenue_by_channel(self, start_date: str | None = None) -> list:
		"""Get revenue breakdown by sales channel."""
		try:
			query = (
				select(
					Sale.sales_channel,
					func.sum(Sale.amount).label("total_revenue"),
					func.count(Sale.id).label("transaction_count"),
					func.avg(Sale.amount).label("avg_transaction"),
				)
				.group_by(Sale.sales_channel)
				.order_by(func.sum(Sale.amount).desc())
			)

			if start_date:
				from datetime import datetime

				start = datetime.fromisoformat(start_date)
				query = query.where(Sale.sale_date >= start)

			result = await self.db.execute(query)
			channels = result.fetchall()

			return [
				{
					"sales_channel": channel.sales_channel,
					"total_revenue": float(channel.total_revenue),
					"transaction_count": channel.transaction_count,
					"avg_transaction": float(channel.avg_transaction),
				}
				for channel in channels
			]
		except Exception:
			return []

	async def get_sales_trends(
		self,
		start_date: str,
		end_date: str,
		group_by: str = "day",
		category: str | None = None,
	) -> dict[str, Any]:
		"""Get sales trends over time with detailed analysis."""
		try:
			from datetime import datetime

			start_dt = datetime.fromisoformat(start_date)
			end_dt = datetime.fromisoformat(end_date).replace(
				hour=23, minute=59, second=59
			)

			if group_by == "day":
				date_trunc = func.date_trunc("day", Sale.sale_date)
			elif group_by == "week":
				date_trunc = func.date_trunc("week", Sale.sale_date)
			elif group_by == "month":
				date_trunc = func.date_trunc("month", Sale.sale_date)
			elif group_by == "quarter":
				date_trunc = func.date_trunc("quarter", Sale.sale_date)
			else:
				date_trunc = func.date_trunc("day", Sale.sale_date)

			query = (
				select(
					date_trunc.label("period"),
					func.sum(Sale.amount).label("total_amount"),
					func.sum(Sale.quantity).label("total_quantity"),
					func.count(Sale.id).label("transaction_count"),
					func.avg(Sale.amount).label("avg_transaction_value"),
				)
				.where(and_(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt))
				.group_by(date_trunc)
				.order_by(date_trunc)
			)

			if category:
				query = query.where(Sale.category == category)

			result = await self.db.execute(query)
			trends = result.fetchall()

			growth_rates = []
			for i in range(1, len(trends)):
				prev_amount = float(trends[i - 1].total_amount or 0)
				curr_amount = float(trends[i].total_amount or 0)
				if prev_amount > 0:
					growth_rate = ((curr_amount - prev_amount) / prev_amount) * 100
				else:
					growth_rate = 0
				growth_rates.append(growth_rate)

			return {
				"trends": [
					{
						"period": trend.period.isoformat(),
						"total_amount": float(trend.total_amount or 0),
						"total_quantity": int(trend.total_quantity or 0),
						"transaction_count": int(trend.transaction_count or 0),
						"avg_transaction_value": float(
							trend.avg_transaction_value or 0
						),
					}
					for trend in trends
				],
				"growth_rates": growth_rates,
				"summary": {
					"total_periods": len(trends),
					"avg_growth_rate": sum(growth_rates) / len(growth_rates)
					if growth_rates
					else 0,
					"best_period": max(
						trends, key=lambda x: x.total_amount or 0
					).period.isoformat()
					if trends
					else None,
					"worst_period": min(
						trends, key=lambda x: x.total_amount or 0
					).period.isoformat()
					if trends
					else None,
				},
			}
		except Exception as e:
			return {
				"error": f"Error getting sales trends: {str(e)}",
				"trends": [],
				"growth_rates": [],
				"summary": {},
			}

	async def get_top_selling_products(
		self,
		start_date: str,
		end_date: str,
		limit: int = 10,
		category: str | None = None,
	) -> dict[str, Any]:
		"""Get top selling products by revenue and quantity."""
		try:
			from datetime import datetime

			start_dt = datetime.fromisoformat(start_date)
			end_dt = datetime.fromisoformat(end_date).replace(
				hour=23, minute=59, second=59
			)

			query = (
				select(
					Sale.product_name,
					Sale.category,
					func.sum(Sale.amount).label("total_revenue"),
					func.sum(Sale.quantity).label("total_quantity"),
					func.count(Sale.id).label("transaction_count"),
					func.avg(Sale.amount).label("avg_price"),
				)
				.where(and_(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt))
				.group_by(Sale.product_name, Sale.category)
				.order_by(desc(func.sum(Sale.amount)))
				.limit(limit)
			)

			if category:
				query = query.where(Sale.category == category)

			result = await self.db.execute(query)
			products = result.fetchall()

			return {
				"top_products": [
					{
						"product_name": product.product_name,
						"category": product.category,
						"total_revenue": float(product.total_revenue or 0),
						"total_quantity": int(product.total_quantity or 0),
						"transaction_count": int(product.transaction_count or 0),
						"avg_price": float(product.avg_price or 0),
					}
					for product in products
				],
				"summary": {
					"total_products": len(products),
					"total_revenue": sum(float(p.total_revenue or 0) for p in products),
					"total_quantity": sum(int(p.total_quantity or 0) for p in products),
				},
			}
		except Exception as e:
			return {
				"error": f"Error getting top products: {str(e)}",
				"top_products": [],
				"summary": {},
			}

	async def get_sales_by_channel(
		self, start_date: str, end_date: str
	) -> dict[str, Any]:
		"""Analyze sales performance by sales channel."""
		try:
			from datetime import datetime

			start_dt = datetime.fromisoformat(start_date)
			end_dt = datetime.fromisoformat(end_date).replace(
				hour=23, minute=59, second=59
			)

			query = (
				select(
					Sale.sales_channel,
					func.sum(Sale.amount).label("total_revenue"),
					func.sum(Sale.quantity).label("total_quantity"),
					func.count(Sale.id).label("transaction_count"),
					func.avg(Sale.amount).label("avg_transaction_value"),
				)
				.where(and_(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt))
				.group_by(Sale.sales_channel)
				.order_by(desc(func.sum(Sale.amount)))
			)

			result = await self.db.execute(query)
			channels = result.fetchall()

			total_revenue = sum(float(c.total_revenue or 0) for c in channels)

			return {
				"channels": [
					{
						"channel": channel.sales_channel,
						"total_revenue": float(channel.total_revenue or 0),
						"total_quantity": int(channel.total_quantity or 0),
						"transaction_count": int(channel.transaction_count or 0),
						"avg_transaction_value": float(
							channel.avg_transaction_value or 0
						),
						"revenue_percentage": (
							float(channel.total_revenue or 0) / total_revenue * 100
						)
						if total_revenue > 0
						else 0,
					}
					for channel in channels
				],
				"summary": {
					"total_channels": len(channels),
					"total_revenue": total_revenue,
					"best_channel": max(
						channels, key=lambda x: x.total_revenue or 0
					).sales_channel
					if channels
					else None,
				},
			}
		except Exception as e:
			return {
				"error": f"Error getting sales by channel: {str(e)}",
				"channels": [],
				"summary": {},
			}
