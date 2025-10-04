"""Customer-specific query builders."""

from typing import Any

from sqlalchemy import desc, func, select

from src.models.customer import Customer
from src.models.sales import Sale

from .base import BaseQueryBuilder


class CustomerQueryBuilder(BaseQueryBuilder):
	"""Specialized query builder for customer operations."""

	@staticmethod
	def build_customer_query(
		filters: dict[str, Any] | None = None, order_by: str | None = None
	):
		"""Build a customer query with common filters."""
		query = select(Customer)

		if not filters:
			return query

		if "customer_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Customer.customer_name, filters["customer_name"]
			)

		if "email" in filters:
			query = query.where(Customer.email == filters["email"])

		if "customer_type" in filters:
			query = query.where(Customer.customer_type == filters["customer_type"])

		if "is_active" in filters:
			query = query.where(Customer.is_active == filters["is_active"])

		if "city" in filters:
			query = query.where(Customer.city == filters["city"])

		if "country" in filters:
			query = query.where(Customer.country == filters["country"])

		if "credit_limit" in filters:
			query = BaseQueryBuilder.apply_range_filter(
				query, Customer.credit_limit, filters["credit_limit"]
			)

		query = BaseQueryBuilder.apply_ordering(
			query, Customer, order_by, Customer.customer_name
		)

		return query

	@staticmethod
	def build_customer_count_query(filters: dict[str, Any] | None = None):
		"""Build a count query for customers with same filters."""
		query = select(func.count(Customer.id))

		if not filters:
			return query

		if "customer_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Customer.customer_name, filters["customer_name"]
			)

		if "email" in filters:
			query = query.where(Customer.email == filters["email"])

		if "customer_type" in filters:
			query = query.where(Customer.customer_type == filters["customer_type"])

		if "is_active" in filters:
			query = query.where(Customer.is_active == filters["is_active"])

		if "city" in filters:
			query = query.where(Customer.city == filters["city"])

		if "country" in filters:
			query = query.where(Customer.country == filters["country"])

		if "credit_limit" in filters:
			query = BaseQueryBuilder.apply_range_filter(
				query, Customer.credit_limit, filters["credit_limit"]
			)

		return query

	@staticmethod
	def build_top_customers_query(limit: int = 10):
		"""Build query for top customers by purchase amount."""
		return (
			select(
				Sale.customer_id,
				Sale.customer_name,
				func.sum(Sale.amount).label("total_purchases"),
				func.count(Sale.id).label("purchase_count"),
				func.avg(Sale.amount).label("avg_purchase"),
			)
			.where(Sale.customer_id.isnot(None))
			.group_by(Sale.customer_id, Sale.customer_name)
			.order_by(desc(func.sum(Sale.amount)))
			.limit(limit)
		)

	@staticmethod
	def build_customer_search_query(search_term: str, limit: int = 20):
		"""Build query for customer search."""
		return (
			select(Customer)
			.where(
				Customer.customer_name.ilike(f"%{search_term}%")
				| Customer.email.ilike(f"%{search_term}%")
				| Customer.company.ilike(f"%{search_term}%")
			)
			.order_by(Customer.customer_name)
			.limit(limit)
		)

	@staticmethod
	def build_customer_purchase_history_query(customer_id: int, limit: int = 50):
		"""Build query for customer purchase history."""
		return (
			select(Sale)
			.where(Sale.customer_id == customer_id)
			.order_by(desc(Sale.sale_date))
			.limit(limit)
		)
