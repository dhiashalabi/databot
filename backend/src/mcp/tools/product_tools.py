"""Product-related tools for MCP server."""

from typing import Any

from sqlalchemy import or_, select

from src.models.product import Category, Product
from src.queries import CategoryQueryBuilder, ProductQueryBuilder

from .base_tools import BaseTools


class ProductTools(BaseTools):
	"""Tools for product data analysis and querying."""

	async def get_top_products(self, limit: int = 10) -> list:
		"""Get top selling products by quantity and revenue."""
		try:
			query = ProductQueryBuilder.build_top_products_query(limit)
			result = await self.db.execute(query)
			products = result.fetchall()

			return [
				{
					"product_id": product.product_id,
					"product_name": product.product_name,
					"total_quantity": product.total_quantity,
					"total_revenue": float(product.total_revenue),
					"sales_count": product.sales_count,
					"avg_price": float(product.avg_price),
				}
				for product in products
			]
		except Exception:
			return []

	async def get_products_low_stock(self, threshold: int = 20) -> list:
		"""Get products with low stock levels."""
		try:
			query = ProductQueryBuilder.build_low_stock_query(threshold)
			result = await self.db.execute(query)
			products = result.scalars().all()

			return [self._format_product_data(product) for product in products]
		except Exception:
			return []

	async def get_products_summary(self) -> dict[str, Any]:
		"""Get overall products summary."""
		try:
			query = ProductQueryBuilder.build_product_summary_query()
			result = await self.db.execute(query)
			summary = result.fetchone()

			return {
				"total_products": summary.total_products,
				"active_products": summary.active_products,
				"avg_price": float(summary.avg_price or 0),
				"total_inventory": summary.total_inventory or 0,
				"low_stock_count": summary.low_stock_count,
			}
		except Exception as e:
			return {"error": f"Error getting products summary: {str(e)}"}

	async def get_product_details(
		self, product_id: int | None = None, product_name: str | None = None
	) -> dict[str, Any] | None:
		"""Get detailed information about a specific product."""
		try:
			query = ProductQueryBuilder.build_product_details_query(
				product_id, product_name
			)
			if not query:
				return None

			result = await self.db.execute(query)
			product = result.scalar_one_or_none()

			if not product:
				return None

			sales_query = ProductQueryBuilder.build_product_sales_query(product.id, 20)
			sales_result = await self.db.execute(sales_query)
			sales = sales_result.scalars().all()

			total_sold = sum(sale.quantity for sale in sales)
			total_revenue = sum(float(sale.amount) for sale in sales)
			avg_sale_price = total_revenue / total_sold if total_sold > 0 else 0

			return {
				"product": self._format_product_data(product),
				"recent_sales": [self._format_sale_data(sale) for sale in sales],
				"metrics": {
					"total_sold": total_sold,
					"total_revenue": total_revenue,
					"avg_sale_price": avg_sale_price,
					"sales_count": len(sales),
					"last_sale": sales[0].sale_date.isoformat() if sales else None,
				},
			}
		except Exception:
			return None

	async def search_products(
		self,
		search_term: str | None = None,
		category: str | None = None,
		low_stock_only: bool = False,
		limit: int = 20,
	) -> list[dict[str, Any]]:
		"""Search products by various criteria."""
		try:
			query = select(Product)

			if search_term:
				search_filter = or_(
					Product.product_name.ilike(f"%{search_term}%"),
					Product.sku.ilike(f"%{search_term}%"),
				)
				query = query.where(search_filter)

			if category:
				query = query.join(Category).where(
					Category.category_name.ilike(f"%{category}%")
				)

			if low_stock_only:
				query = query.where(Product.stock_quantity <= Product.reorder_level)

			query = query.limit(limit).order_by(Product.product_name)

			result = await self.db.execute(query)
			products = result.scalars().all()

			return [self._format_product_data(product) for product in products]
		except Exception:
			return []

	async def get_products(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get products with flexible filtering by any property."""
		try:
			query = ProductQueryBuilder.build_product_query(filters, order_by)
			query = ProductQueryBuilder.apply_pagination(query, limit, offset)

			result = await self.db.execute(query)
			products = result.scalars().all()

			count_query = ProductQueryBuilder.build_product_count_query(filters)
			count_result = await self.db.execute(count_query)
			total_count = count_result.scalar()

			products_data = [self._format_product_data(product) for product in products]

			return {
				"products": products_data,
				"summary": {
					"total_count": total_count,
					"returned_count": len(products_data),
					"active_count": sum(1 for p in products if p.is_active),
					"total_inventory_value": sum(
						float(p.stock_quantity * (p.cost_price or p.unit_price))
						for p in products
					),
					"low_stock_count": sum(
						1 for p in products if p.stock_quantity <= p.reorder_level
					),
				},
			}
		except Exception as e:
			return {
				"error": f"Error querying products: {str(e)}",
				"error_type": type(e).__name__,
				"products": [],
				"summary": {
					"total_count": 0,
					"returned_count": 0,
					"active_count": 0,
					"total_inventory_value": 0,
					"low_stock_count": 0,
				},
			}

	async def get_categories(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get categories with flexible filtering by any property."""
		try:
			query = CategoryQueryBuilder.build_category_query(filters, order_by)
			query = CategoryQueryBuilder.apply_pagination(query, limit, offset)

			result = await self.db.execute(query)
			categories = result.scalars().all()

			count_query = CategoryQueryBuilder.build_category_count_query(filters)
			count_result = await self.db.execute(count_query)
			total_count = count_result.scalar()

			categories_data = [
				self._format_category_data(category) for category in categories
			]

			return {
				"categories": categories_data,
				"summary": {
					"total_count": total_count,
					"returned_count": len(categories_data),
					"active_count": sum(1 for c in categories if c.is_active),
					"parent_categories": sum(
						1 for c in categories if c.parent_category_id is None
					),
				},
			}
		except Exception as e:
			return {
				"error": f"Error querying categories: {str(e)}",
				"error_type": type(e).__name__,
				"categories": [],
				"summary": {
					"total_count": 0,
					"returned_count": 0,
					"active_count": 0,
					"parent_categories": 0,
				},
			}
