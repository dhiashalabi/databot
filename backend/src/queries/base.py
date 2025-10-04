"""Base query builder with common query patterns."""

from datetime import datetime
from typing import Any

from sqlalchemy import desc, func, select


class BaseQueryBuilder:
	"""Base query builder with common query patterns."""

	@staticmethod
	def apply_range_filter(query, field, range_filter):
		"""Apply range filters (min/max) to a query."""
		if isinstance(range_filter, dict):
			if "min" in range_filter:
				query = query.where(field >= range_filter["min"])
			if "max" in range_filter:
				query = query.where(field <= range_filter["max"])
		return query

	@staticmethod
	def apply_like_filter(query, field, like_filter):
		"""Apply LIKE filters to a query."""
		if isinstance(like_filter, dict) and "like" in like_filter:
			query = query.where(field.like(f"%{like_filter['like']}%"))
		else:
			query = query.where(field == like_filter)
		return query

	@staticmethod
	def apply_date_filter(query, field, date_filter):
		"""Apply date range filters to a query."""
		if isinstance(date_filter, dict):
			if "min" in date_filter:
				min_date = datetime.fromisoformat(date_filter["min"])
				query = query.where(field >= min_date)
			if "max" in date_filter:
				max_date = datetime.fromisoformat(date_filter["max"])
				query = query.where(field <= max_date)
		return query

	@staticmethod
	def apply_ordering(
		query, model_class, order_by: str | None = None, default_order=None
	):
		"""Apply ordering to a query."""
		if order_by and hasattr(model_class, order_by):
			order_field = getattr(model_class, order_by)
			query = query.order_by(desc(order_field))
		elif default_order:
			query = query.order_by(default_order)
		return query

	@staticmethod
	def apply_pagination(query, limit: int | None = None, offset: int = 0):
		"""Apply pagination to a query."""
		if limit:
			query = query.limit(limit)
		if offset:
			query = query.offset(offset)
		return query

	@staticmethod
	def build_count_query(base_query, filters: dict[str, Any] | None = None):
		"""Convert a base query to a count query."""
		model = base_query.column_descriptions[0]["entity"]
		return select(func.count(model.id))
