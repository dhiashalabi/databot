"""Sales-specific query builders."""

from typing import Any

from sqlalchemy import desc, func, select

from src.models.sales import Sale

from .base import BaseQueryBuilder


class SalesQueryBuilder(BaseQueryBuilder):
	"""Specialized query builder for sales operations."""

	@staticmethod
	def build_sales_query(
		filters: dict[str, Any] | None = None, order_by: str | None = None
	):
		"""Build a sales query with common filters."""
		query = select(Sale)

		if not filters:
			return query

		if "amount" in filters and isinstance(filters["amount"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Sale.amount, filters["amount"]
			)

		if "category" in filters:
			query = query.where(Sale.category == filters["category"])

		if "product_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Sale.product_name, filters["product_name"]
			)

		if "payment_status" in filters:
			query = query.where(Sale.payment_status == filters["payment_status"])

		if "sales_channel" in filters:
			query = query.where(Sale.sales_channel == filters["sales_channel"])

		if "customer_id" in filters:
			query = query.where(Sale.customer_id == filters["customer_id"])

		if "product_id" in filters:
			query = query.where(Sale.product_id == filters["product_id"])

		if "sale_date" in filters and isinstance(filters["sale_date"], dict):
			query = BaseQueryBuilder.apply_date_filter(
				query, Sale.sale_date, filters["sale_date"]
			)

		query = BaseQueryBuilder.apply_ordering(
			query, Sale, order_by, desc(Sale.sale_date)
		)

		return query

	@staticmethod
	def build_sales_count_query(filters: dict[str, Any] | None = None):
		"""Build a count query for sales with same filters."""
		query = select(func.count(Sale.id))

		if not filters:
			return query

		if "amount" in filters and isinstance(filters["amount"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Sale.amount, filters["amount"]
			)

		if "category" in filters:
			query = query.where(Sale.category == filters["category"])

		if "product_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Sale.product_name, filters["product_name"]
			)

		if "payment_status" in filters:
			query = query.where(Sale.payment_status == filters["payment_status"])

		if "sales_channel" in filters:
			query = query.where(Sale.sales_channel == filters["sales_channel"])

		if "customer_id" in filters:
			query = query.where(Sale.customer_id == filters["customer_id"])

		if "product_id" in filters:
			query = query.where(Sale.product_id == filters["product_id"])

		if "sale_date" in filters and isinstance(filters["sale_date"], dict):
			query = BaseQueryBuilder.apply_date_filter(
				query, Sale.sale_date, filters["sale_date"]
			)

		return query

	@staticmethod
	def build_sales_by_period_query(start_date: str, end_date: str | None = None):
		"""Build query for sales in a specific period."""
		from datetime import datetime

		query = select(Sale)
		start = datetime.fromisoformat(start_date)
		query = query.where(Sale.sale_date >= start)

		if end_date:
			end = datetime.fromisoformat(end_date)
			query = query.where(Sale.sale_date <= end)

		return query.order_by(desc(Sale.sale_date))

	@staticmethod
	def build_sales_by_category_query(start_date: str | None = None):
		"""Build query for sales grouped by category."""
		from datetime import datetime

		query = select(
			Sale.category,
			func.sum(Sale.amount).label("total_amount"),
			func.count(Sale.id).label("sales_count"),
			func.avg(Sale.amount).label("avg_amount"),
		).group_by(Sale.category)

		if start_date:
			start = datetime.fromisoformat(start_date)
			query = query.where(Sale.sale_date >= start)

		return query

	@staticmethod
	def build_top_products_query(limit: int = 10, start_date: str | None = None):
		"""Build query for top selling products."""
		from datetime import datetime

		query = select(
			Sale.product_id,
			Sale.product_name,
			func.sum(Sale.quantity).label("total_quantity"),
			func.sum(Sale.amount).label("total_revenue"),
			func.count(Sale.id).label("sales_count"),
			func.avg(Sale.amount).label("avg_price"),
		).where(Sale.product_id.isnot(None))

		if start_date:
			start = datetime.fromisoformat(start_date)
			query = query.where(Sale.sale_date >= start)

		return (
			query.group_by(Sale.product_id, Sale.product_name)
			.order_by(desc(func.sum(Sale.quantity)))
			.limit(limit)
		)

	@staticmethod
	def build_sales_trends_query(period: str = "month", limit: int = 12):
		"""Build query for sales trends over time."""
		if period == "day":
			date_trunc = func.date_trunc("day", Sale.sale_date)
		elif period == "week":
			date_trunc = func.date_trunc("week", Sale.sale_date)
		elif period == "month":
			date_trunc = func.date_trunc("month", Sale.sale_date)
		elif period == "year":
			date_trunc = func.date_trunc("year", Sale.sale_date)
		else:
			date_trunc = func.date_trunc("month", Sale.sale_date)

		return (
			select(
				date_trunc.label("period"),
				func.sum(Sale.amount).label("total_revenue"),
				func.count(Sale.id).label("sales_count"),
				func.avg(Sale.amount).label("avg_sale"),
			)
			.group_by(date_trunc)
			.order_by(desc(date_trunc))
			.limit(limit)
		)
