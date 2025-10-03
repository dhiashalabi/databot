"""MCP tools for database operations."""

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.product import Category, Product
from src.models.sales import Sale


class MCPTools:
	"""General purpose tools for querying database - exposed to OpenAI via function calling."""

	def __init__(self, db: AsyncSession):
		"""Initialize with database session."""
		self.db = db

	async def get_sales_by_period(
		self, start_date: str, end_date: str, category: str | None = None
	) -> dict:
		"""Get total sales for a specific period.

		Args:
			start_date: Start date in ISO format (YYYY-MM-DD)
			end_date: End date in ISO format (YYYY-MM-DD)
			category: Optional category filter

		Returns:
			Dictionary with total_amount, total_quantity, and count

		"""
		start_dt = datetime.strptime(start_date, "%Y-%m-%d")
		end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
			hour=23, minute=59, second=59
		)

		query = select(
			func.sum(Sale.amount).label("total_amount"),
			func.sum(Sale.quantity).label("total_quantity"),
			func.count(Sale.id).label("count"),
		).where(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt)

		if category:
			query = query.where(Sale.category == category)

		result = await self.db.execute(query)
		row = result.first()

		return {
			"total_amount": float(row.total_amount or 0),
			"total_quantity": int(row.total_quantity or 0),
			"count": int(row.count or 0),
			"period": {"start": start_date, "end": end_date},
		}

	async def compare_sales_periods(
		self, period1_start: str, period1_end: str, period2_start: str, period2_end: str
	) -> dict:
		"""Compare sales between two periods.

		Args:
			period1_start: Period 1 start date (YYYY-MM-DD)
			period1_end: Period 1 end date (YYYY-MM-DD)
			period2_start: Period 2 start date (YYYY-MM-DD)
			period2_end: Period 2 end date (YYYY-MM-DD)

		Returns:
			Dictionary comparing both periods

		"""
		period1 = await self.get_sales_by_period(period1_start, period1_end)
		period2 = await self.get_sales_by_period(period2_start, period2_end)

		amount_change = period2["total_amount"] - period1["total_amount"]
		amount_change_pct = (
			(amount_change / period1["total_amount"] * 100)
			if period1["total_amount"] > 0
			else 0
		)

		return {
			"period1": period1,
			"period2": period2,
			"comparison": {
				"amount_change": amount_change,
				"amount_change_percentage": round(amount_change_pct, 2),
				"quantity_change": period2["total_quantity"]
				- period1["total_quantity"],
			},
		}

	async def get_sales_by_category(self, start_date: str | None = None) -> list:
		"""Get sales breakdown by category.

		Args:
			start_date: Optional start date filter (YYYY-MM-DD)

		Returns:
			List of categories with sales data

		"""
		query = (
			select(
				Sale.category,
				func.sum(Sale.amount).label("total_amount"),
				func.sum(Sale.quantity).label("total_quantity"),
				func.count(Sale.id).label("sales_count"),
			)
			.where(Sale.category.isnot(None))
			.group_by(Sale.category)
			.order_by(func.sum(Sale.amount).desc())
		)

		if start_date:
			start_dt = datetime.strptime(start_date, "%Y-%m-%d")
			query = query.where(Sale.sale_date >= start_dt)

		result = await self.db.execute(query)
		rows = result.all()

		return [
			{
				"category": row.category,
				"total_amount": float(row.total_amount),
				"total_quantity": int(row.total_quantity),
				"sales_count": int(row.sales_count),
			}
			for row in rows
		]

	async def get_top_products(
		self, limit: int = 10, start_date: str | None = None
	) -> list:
		"""Get top selling products by revenue.

		Args:
			limit: Number of top products to return
			start_date: Optional start date filter (YYYY-MM-DD)

		Returns:
			List of top products with sales data

		"""
		query = (
			select(
				Sale.product_name,
				func.sum(Sale.amount).label("total_amount"),
				func.sum(Sale.quantity).label("total_quantity"),
				func.count(Sale.id).label("sales_count"),
			)
			.group_by(Sale.product_name)
			.order_by(func.sum(Sale.amount).desc())
			.limit(limit)
		)

		if start_date:
			start_dt = datetime.strptime(start_date, "%Y-%m-%d")
			query = query.where(Sale.sale_date >= start_dt)

		result = await self.db.execute(query)
		rows = result.all()

		return [
			{
				"product_name": row.product_name,
				"total_amount": float(row.total_amount),
				"total_quantity": int(row.total_quantity),
				"sales_count": int(row.sales_count),
			}
			for row in rows
		]

	async def get_products_low_stock(self, threshold: int = 20) -> list:
		"""Get products with stock below threshold.

		Args:
			threshold: Stock quantity threshold (default: 20)

		Returns:
			List of products with low stock

		"""
		query = (
			select(Product)
			.where(Product.stock_quantity <= threshold)
			.where(Product.is_active)
			.order_by(Product.stock_quantity.asc())
		)

		result = await self.db.execute(query)
		products = result.scalars().all()

		return [
			{
				"product_name": p.product_name,
				"sku": p.sku,
				"stock_quantity": p.stock_quantity,
				"reorder_level": p.reorder_level,
				"unit_price": float(p.unit_price),
			}
			for p in products
		]

	async def get_top_customers(
		self, limit: int = 10, start_date: str | None = None
	) -> list:
		"""Get top customers by total spending.

		Args:
			limit: Number of top customers to return
			start_date: Optional start date filter (YYYY-MM-DD)

		Returns:
			List of top customers with spending data

		"""
		query = (
			select(
				Sale.customer_name,
				func.sum(Sale.amount).label("total_spent"),
				func.count(Sale.id).label("purchase_count"),
				func.avg(Sale.amount).label("avg_purchase"),
			)
			.where(Sale.customer_name.isnot(None))
			.group_by(Sale.customer_name)
			.order_by(func.sum(Sale.amount).desc())
			.limit(limit)
		)

		if start_date:
			start_dt = datetime.strptime(start_date, "%Y-%m-%d")
			query = query.where(Sale.sale_date >= start_dt)

		result = await self.db.execute(query)
		rows = result.all()

		return [
			{
				"customer_name": row.customer_name,
				"total_spent": float(row.total_spent),
				"purchase_count": int(row.purchase_count),
				"avg_purchase": float(row.avg_purchase),
			}
			for row in rows
		]

	async def get_customer_details(self, customer_name: str) -> dict | None:
		"""Get detailed information about a specific customer.

		Args:
			customer_name: Name of the customer

		Returns:
			Customer details with purchase history

		"""
		customer_query = select(Customer).where(
			Customer.customer_name.ilike(f"%{customer_name}%")
		)
		customer_result = await self.db.execute(customer_query)
		customer = customer_result.scalar_one_or_none()

		if not customer:
			return None

		sales_query = select(
			func.count(Sale.id).label("total_purchases"),
			func.sum(Sale.amount).label("total_spent"),
			func.max(Sale.sale_date).label("last_purchase"),
		).where(Sale.customer_id == customer.id)

		sales_result = await self.db.execute(sales_query)
		stats = sales_result.first()

		return {
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
			"total_purchases": int(stats.total_purchases or 0),
			"total_spent": float(stats.total_spent or 0),
			"last_purchase": stats.last_purchase.isoformat()
			if stats.last_purchase
			else None,
		}

	async def get_pending_invoices(self) -> list:
		"""Get all pending/unpaid invoices.

		Returns:
			List of pending invoices

		"""
		query = (
			select(Invoice)
			.where(Invoice.status == "pending")
			.order_by(Invoice.due_date.asc())
		)

		result = await self.db.execute(query)
		invoices = result.scalars().all()

		return [
			{
				"invoice_number": inv.invoice_number,
				"invoice_date": inv.invoice_date.isoformat(),
				"due_date": inv.due_date.isoformat() if inv.due_date else None,
				"total_amount": float(inv.total_amount),
				"status": inv.status,
			}
			for inv in invoices
		]

	async def get_invoice_summary(self, start_date: str | None = None) -> dict:
		"""Get invoice summary statistics.

		Args:
			start_date: Optional start date filter (YYYY-MM-DD)

		Returns:
			Invoice summary with totals by status

		"""
		query = select(
			Invoice.status,
			func.count(Invoice.id).label("count"),
			func.sum(Invoice.total_amount).label("total_amount"),
		).group_by(Invoice.status)

		if start_date:
			start_dt = datetime.strptime(start_date, "%Y-%m-%d")
			query = query.where(Invoice.invoice_date >= start_dt)

		result = await self.db.execute(query)
		rows = result.all()

		summary = {
			"by_status": [
				{
					"status": row.status,
					"count": int(row.count),
					"total_amount": float(row.total_amount),
				}
				for row in rows
			]
		}

		total_invoices = sum(item["count"] for item in summary["by_status"])
		total_amount = sum(item["total_amount"] for item in summary["by_status"])

		summary["totals"] = {
			"total_invoices": total_invoices,
			"total_amount": total_amount,
		}

		return summary

	async def get_revenue_by_channel(self, start_date: str | None = None) -> list:
		"""Get revenue breakdown by sales channel.

		Args:
			start_date: Optional start date filter (YYYY-MM-DD)

		Returns:
			List of sales channels with revenue data

		"""
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
			start_dt = datetime.strptime(start_date, "%Y-%m-%d")
			query = query.where(Sale.sale_date >= start_dt)

		result = await self.db.execute(query)
		rows = result.all()

		return [
			{
				"sales_channel": row.sales_channel,
				"total_revenue": float(row.total_revenue),
				"transaction_count": int(row.transaction_count),
				"avg_transaction": float(row.avg_transaction),
			}
			for row in rows
		]

	async def get_sales_summary(self) -> dict:
		"""Get overall sales summary for MCP resources."""
		query = select(
			func.sum(Sale.amount).label("total_revenue"),
			func.count(Sale.id).label("total_transactions"),
			func.avg(Sale.amount).label("avg_transaction_value"),
			func.max(Sale.sale_date).label("last_sale"),
		)

		result = await self.db.execute(query)
		row = result.first()

		return {
			"total_revenue": float(row.total_revenue or 0),
			"total_transactions": int(row.total_transactions or 0),
			"avg_transaction_value": float(row.avg_transaction_value or 0),
			"last_sale": row.last_sale.isoformat() if row.last_sale else None,
		}

	async def get_customers_summary(self) -> dict:
		"""Get overall customers summary for MCP resources."""
		query = select(
			func.count(Customer.id).label("total_customers"),
			func.count(Customer.id)
			.filter(Customer.created_at >= datetime.now().replace(day=1))
			.label("new_this_month"),
		)

		result = await self.db.execute(query)
		row = result.first()

		return {
			"total_customers": int(row.total_customers or 0),
			"new_this_month": int(row.new_this_month or 0),
		}

	async def get_products_summary(self) -> dict:
		"""Get overall products summary for MCP resources."""
		query = select(
			func.count(Product.id).label("total_products"),
			func.count(Product.id).filter(Product.is_active).label("active_products"),
			func.avg(Product.price).label("avg_price"),
		)

		result = await self.db.execute(query)
		row = result.first()

		return {
			"total_products": int(row.total_products or 0),
			"active_products": int(row.active_products or 0),
			"avg_price": float(row.avg_price or 0),
		}

	async def get_product_details(
		self, product_name: str | None = None, product_id: str | None = None
	) -> dict | None:
		"""Get detailed information about a specific product.

		Args:
			product_name: Name of the product (partial matches supported)
			product_id: ID of the product

		Returns:
			Product details with performance metrics

		"""
		query = select(Product)

		if product_id:
			query = query.where(Product.id == int(product_id))
		elif product_name:
			query = query.where(Product.product_name.ilike(f"%{product_name}%"))
		else:
			return None

		result = await self.db.execute(query)
		product = result.scalar_one_or_none()

		if not product:
			return None

		# Get sales statistics for this product
		sales_query = select(
			func.count(Sale.id).label("total_sales"),
			func.sum(Sale.amount).label("total_revenue"),
			func.sum(Sale.quantity).label("total_quantity_sold"),
			func.max(Sale.sale_date).label("last_sale"),
		).where(Sale.product_id == product.id)

		sales_result = await self.db.execute(sales_query)
		stats = sales_result.first()

		return {
			"product_id": product.id,
			"product_name": product.product_name,
			"sku": product.sku,
			"description": product.description,
			"unit_price": float(product.unit_price),
			"cost_price": float(product.cost_price or 0),
			"stock_quantity": product.stock_quantity,
			"reorder_level": product.reorder_level,
			"is_active": product.is_active,
			"category_id": product.category_id,
			"total_sales": int(stats.total_sales or 0),
			"total_revenue": float(stats.total_revenue or 0),
			"total_quantity_sold": int(stats.total_quantity_sold or 0),
			"last_sale": stats.last_sale.isoformat() if stats.last_sale else None,
		}

	async def search_customers(
		self,
		search_term: str | None = None,
		customer_type: str | None = None,
		limit: int = 20,
	) -> list:
		"""Search customers by various criteria.

		Args:
			search_term: Search term to match against customer name, email, or company
			customer_type: Filter by customer type
			limit: Maximum number of results to return

		Returns:
			List of matching customers

		"""
		query = select(Customer)

		if search_term:
			search_filter = or_(
				Customer.customer_name.ilike(f"%{search_term}%"),
				Customer.email.ilike(f"%{search_term}%"),
				Customer.company.ilike(f"%{search_term}%"),
			)
			query = query.where(search_filter)

		if customer_type:
			query = query.where(Customer.customer_type == customer_type)

		query = query.limit(limit).order_by(Customer.customer_name)

		result = await self.db.execute(query)
		customers = result.scalars().all()

		return [
			{
				"id": customer.id,
				"customer_name": customer.customer_name,
				"email": customer.email,
				"phone": customer.phone,
				"company": customer.company,
				"customer_type": customer.customer_type,
				"is_active": customer.is_active,
			}
			for customer in customers
		]

	async def search_products(
		self,
		search_term: str | None = None,
		category: str | None = None,
		low_stock_only: bool = False,
		limit: int = 20,
	) -> list:
		"""Search products by various criteria.

		Args:
			search_term: Search term to match against product name or SKU
			category: Filter by product category
			low_stock_only: Only return products with low stock
			limit: Maximum number of results to return

		Returns:
			List of matching products

		"""
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

		return [
			{
				"product_id": product.id,
				"product_name": product.product_name,
				"sku": product.sku,
				"unit_price": float(product.unit_price),
				"stock_quantity": product.stock_quantity,
				"reorder_level": product.reorder_level,
				"is_active": product.is_active,
				"category_id": product.category_id,
			}
			for product in products
		]

	async def get_customer_purchase_history(
		self,
		customer_name: str,
		start_date: str | None = None,
		end_date: str | None = None,
		limit: int = 50,
	) -> dict | None:
		"""Get detailed purchase history for a specific customer.

		Args:
			customer_name: Name of the customer
			start_date: Start date for purchase history (YYYY-MM-DD)
			end_date: End date for purchase history (YYYY-MM-DD)
			limit: Maximum number of purchases to return

		Returns:
			Customer purchase history with detailed transactions

		"""
		# First find the customer
		customer_query = select(Customer).where(
			Customer.customer_name.ilike(f"%{customer_name}%")
		)
		customer_result = await self.db.execute(customer_query)
		customer = customer_result.scalar_one_or_none()

		if not customer:
			return None

		# Get purchase history
		query = select(Sale).where(Sale.customer_id == customer.id)

		if start_date:
			start_dt = datetime.strptime(start_date, "%Y-%m-%d")
			query = query.where(Sale.sale_date >= start_dt)

		if end_date:
			end_dt = datetime.strptime(end_date, "%Y-%m-%d")
			query = query.where(Sale.sale_date <= end_dt)

		query = query.order_by(Sale.sale_date.desc()).limit(limit)

		result = await self.db.execute(query)
		sales = result.scalars().all()

		# Calculate summary statistics
		summary_query = select(
			func.count(Sale.id).label("total_purchases"),
			func.sum(Sale.amount).label("total_spent"),
			func.avg(Sale.amount).label("avg_purchase"),
			func.min(Sale.sale_date).label("first_purchase"),
			func.max(Sale.sale_date).label("last_purchase"),
		).where(Sale.customer_id == customer.id)

		if start_date:
			start_dt = datetime.strptime(start_date, "%Y-%m-%d")
			summary_query = summary_query.where(Sale.sale_date >= start_dt)

		if end_date:
			end_dt = datetime.strptime(end_date, "%Y-%m-%d")
			summary_query = summary_query.where(Sale.sale_date <= end_dt)

		summary_result = await self.db.execute(summary_query)
		summary = summary_result.first()

		return {
			"customer": {
				"id": customer.id,
				"customer_name": customer.customer_name,
				"email": customer.email,
				"company": customer.company,
			},
			"summary": {
				"total_purchases": int(summary.total_purchases or 0),
				"total_spent": float(summary.total_spent or 0),
				"avg_purchase": float(summary.avg_purchase or 0),
				"first_purchase": summary.first_purchase.isoformat()
				if summary.first_purchase
				else None,
				"last_purchase": summary.last_purchase.isoformat()
				if summary.last_purchase
				else None,
			},
			"purchases": [
				{
					"sale_id": sale.id,
					"product_name": sale.product_name,
					"amount": float(sale.amount),
					"quantity": sale.quantity,
					"sale_date": sale.sale_date.isoformat(),
					"category": sale.category,
					"payment_status": sale.payment_status,
					"sales_channel": sale.sales_channel,
				}
				for sale in sales
			],
		}
