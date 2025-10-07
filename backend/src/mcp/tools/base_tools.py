"""Base tools class with common functionality for all MCP tools."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class BaseTools:
	"""Base class providing common functionality for all MCP tools."""

	def __init__(self, db: AsyncSession):
		"""Initialize with database session."""
		self.db = db

	async def _safe_execute_query(self, query):
		"""Execute a query with transaction rollback safety."""
		try:
			await self.db.rollback()
			return await self.db.execute(query)
		except Exception as e:
			await self.db.rollback()
			raise e

	async def _execute_query_with_count(
		self,
		query,
		count_query,
		formatter_func,
		error_message: str = "Error executing query",
	) -> dict[str, Any]:
		"""Execute a query with count and format results."""
		try:
			result = await self._safe_execute_query(query)
			items = result.scalars().all()

			count_result = await self._safe_execute_query(count_query)
			total_count = count_result.scalar()

			formatted_items = [formatter_func(item) for item in items]

			return {
				"data": formatted_items,
				"summary": {
					"total_count": total_count,
					"returned_count": len(formatted_items),
				},
			}
		except Exception as e:
			return {
				"error": f"{error_message}: {str(e)}",
				"error_type": type(e).__name__,
				"data": [],
				"summary": {
					"total_count": 0,
					"returned_count": 0,
				},
			}

	async def _apply_date_filters(self, query, date_field, date_filter):
		"""Apply date range filters to a query."""
		if isinstance(date_filter, dict):
			if "min" in date_filter:
				min_date = datetime.fromisoformat(date_filter["min"])
				query = query.where(date_field >= min_date)
			if "max" in date_filter:
				max_date = datetime.fromisoformat(date_filter["max"])
				query = query.where(date_field <= max_date)
		return query

	async def _apply_range_filters(self, query, field, range_filter):
		"""Apply range filters (min/max) to a query."""
		if isinstance(range_filter, dict):
			if "min" in range_filter:
				query = query.where(field >= range_filter["min"])
			if "max" in range_filter:
				query = query.where(field <= range_filter["max"])
		return query

	async def _apply_like_filters(self, query, field, like_filter):
		"""Apply LIKE filters to a query."""
		if isinstance(like_filter, dict) and "like" in like_filter:
			query = query.where(field.like(f"%{like_filter['like']}%"))
		else:
			query = query.where(field == like_filter)
		return query

	def _format_sale_data(self, sale) -> dict[str, Any]:
		"""Format sale data for response."""
		return {
			"id": sale.id,
			"customer_id": sale.customer_id,
			"product_id": sale.product_id,
			"invoice_id": sale.invoice_id,
			"product_name": sale.product_name,
			"amount": float(sale.amount),
			"quantity": sale.quantity,
			"sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
			"customer_name": sale.customer_name,
			"category": sale.category,
			"payment_status": sale.payment_status,
			"sales_channel": sale.sales_channel,
			"created_at": sale.created_at.isoformat() if sale.created_at else None,
		}

	def _format_customer_data(self, customer) -> dict[str, Any]:
		"""Format customer data for response."""
		return {
			"id": customer.id,
			"customer_name": customer.customer_name,
			"email": customer.email,
			"phone": customer.phone,
			"company": customer.company,
			"address": customer.address,
			"city": customer.city,
			"country": customer.country,
			"customer_type": customer.customer_type,
			"credit_limit": float(customer.credit_limit),
			"is_active": customer.is_active,
			"created_at": customer.created_at.isoformat(),
			"updated_at": customer.updated_at.isoformat(),
		}

	def _format_product_data(self, product) -> dict[str, Any]:
		"""Format product data for response."""
		return {
			"id": product.id,
			"product_name": product.product_name,
			"sku": product.sku,
			"description": product.description,
			"category_id": product.category_id,
			"unit_price": float(product.unit_price),
			"cost_price": float(product.cost_price) if product.cost_price else None,
			"stock_quantity": product.stock_quantity,
			"reorder_level": product.reorder_level,
			"is_active": product.is_active,
			"created_at": product.created_at.isoformat(),
			"updated_at": product.updated_at.isoformat(),
		}

	def _format_invoice_data(self, invoice) -> dict[str, Any]:
		"""Format invoice data for response."""
		return {
			"id": invoice.id,
			"invoice_number": invoice.invoice_number,
			"customer_id": invoice.customer_id,
			"invoice_date": invoice.invoice_date.isoformat(),
			"due_date": invoice.due_date.isoformat() if invoice.due_date else None,
			"subtotal": float(invoice.subtotal),
			"tax_amount": float(invoice.tax_amount),
			"discount_amount": float(invoice.discount_amount),
			"total_amount": float(invoice.total_amount),
			"status": invoice.status,
			"payment_method": invoice.payment_method,
			"notes": invoice.notes,
			"created_at": invoice.created_at.isoformat(),
			"updated_at": invoice.updated_at.isoformat(),
		}

	def _format_category_data(self, category) -> dict[str, Any]:
		"""Format category data for response."""
		return {
			"id": category.id,
			"category_name": category.category_name,
			"description": category.description,
			"parent_category_id": category.parent_category_id,
			"is_active": category.is_active,
			"created_at": category.created_at.isoformat(),
		}
