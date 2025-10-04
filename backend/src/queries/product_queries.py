"""Product-specific query builders."""

from typing import Any

from sqlalchemy import func, select

from src.models.product import Category, Product

from .base import BaseQueryBuilder


class ProductQueryBuilder(BaseQueryBuilder):
	"""Specialized query builder for product operations."""

	@staticmethod
	def build_product_query(
		filters: dict[str, Any] | None = None, order_by: str | None = None
	):
		"""Build a product query with common filters."""
		query = select(Product)

		if not filters:
			return query

		if "product_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Product.product_name, filters["product_name"]
			)

		if "sku" in filters:
			query = query.where(Product.sku == filters["sku"])

		if "category_id" in filters:
			query = query.where(Product.category_id == filters["category_id"])

		if "is_active" in filters:
			query = query.where(Product.is_active == filters["is_active"])

		if "unit_price" in filters and isinstance(filters["unit_price"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Product.unit_price, filters["unit_price"]
			)

		if "stock_quantity" in filters and isinstance(filters["stock_quantity"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Product.stock_quantity, filters["stock_quantity"]
			)

		if "reorder_level" in filters and isinstance(filters["reorder_level"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Product.reorder_level, filters["reorder_level"]
			)

		query = BaseQueryBuilder.apply_ordering(
			query, Product, order_by, Product.product_name
		)

		return query

	@staticmethod
	def build_product_count_query(filters: dict[str, Any] | None = None):
		"""Build a count query for products with same filters."""
		query = select(func.count(Product.id))

		if not filters:
			return query

		if "product_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Product.product_name, filters["product_name"]
			)

		if "sku" in filters:
			query = query.where(Product.sku == filters["sku"])

		if "category_id" in filters:
			query = query.where(Product.category_id == filters["category_id"])

		if "is_active" in filters:
			query = query.where(Product.is_active == filters["is_active"])

		if "unit_price" in filters and isinstance(filters["unit_price"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Product.unit_price, filters["unit_price"]
			)

		if "stock_quantity" in filters and isinstance(filters["stock_quantity"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Product.stock_quantity, filters["stock_quantity"]
			)

		if "reorder_level" in filters and isinstance(filters["reorder_level"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Product.reorder_level, filters["reorder_level"]
			)

		return query

	@staticmethod
	def build_low_stock_query(threshold: int = 20):
		"""Build query for products with low stock."""
		return (
			select(Product)
			.where(Product.stock_quantity <= threshold)
			.where(Product.is_active)
			.order_by(Product.stock_quantity)
		)

	@staticmethod
	def build_product_search_query(search_term: str, limit: int = 20):
		"""Build query for product search."""
		return (
			select(Product)
			.where(
				Product.product_name.ilike(f"%{search_term}%")
				| Product.sku.ilike(f"%{search_term}%")
				| Product.description.ilike(f"%{search_term}%")
			)
			.order_by(Product.product_name)
			.limit(limit)
		)

	@staticmethod
	def build_top_products_query(limit: int = 10, start_date: str | None = None):
		"""Build query for top selling products."""
		from datetime import datetime

		from sqlalchemy import desc

		from src.models.sales import Sale

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
	def build_product_summary_query():
		"""Build query for product summary statistics."""
		return select(
			func.count(Product.id).label("total_products"),
			func.count(Product.id).filter(Product.is_active).label("active_products"),
			func.avg(Product.unit_price).label("avg_price"),
			func.sum(Product.stock_quantity).label("total_inventory"),
			func.count(Product.id)
			.filter(Product.stock_quantity <= Product.reorder_level)
			.label("low_stock_count"),
		)

	@staticmethod
	def build_product_details_query(
		product_id: int | None = None, product_name: str | None = None
	):
		"""Build query for product details."""
		query = select(Product)

		if product_id:
			query = query.where(Product.id == product_id)
		elif product_name:
			query = query.where(Product.product_name.ilike(f"%{product_name}%"))
		else:
			return None

		return query

	@staticmethod
	def build_product_sales_query(product_id: int, limit: int = 20):
		"""Build query for product sales history."""
		from sqlalchemy import desc

		from src.models.sales import Sale

		return (
			select(Sale)
			.where(Sale.product_id == product_id)
			.order_by(desc(Sale.sale_date))
			.limit(limit)
		)


class CategoryQueryBuilder(BaseQueryBuilder):
	"""Specialized query builder for category operations."""

	@staticmethod
	def build_category_query(
		filters: dict[str, Any] | None = None, order_by: str | None = None
	):
		"""Build a category query with common filters."""
		query = select(Category)

		if not filters:
			return query

		if "category_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Category.category_name, filters["category_name"]
			)

		if "is_active" in filters:
			query = query.where(Category.is_active == filters["is_active"])

		if "parent_category_id" in filters:
			query = query.where(
				Category.parent_category_id == filters["parent_category_id"]
			)

		if "description" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Category.description, filters["description"]
			)

		query = BaseQueryBuilder.apply_ordering(
			query, Category, order_by, Category.category_name
		)

		return query

	@staticmethod
	def build_category_count_query(filters: dict[str, Any] | None = None):
		"""Build a count query for categories with same filters."""
		query = select(func.count(Category.id))

		if not filters:
			return query

		if "category_name" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Category.category_name, filters["category_name"]
			)

		if "is_active" in filters:
			query = query.where(Category.is_active == filters["is_active"])

		if "parent_category_id" in filters:
			query = query.where(
				Category.parent_category_id == filters["parent_category_id"]
			)

		if "description" in filters:
			query = BaseQueryBuilder.apply_like_filter(
				query, Category.description, filters["description"]
			)

		return query
