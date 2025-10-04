"""Customer-related tools for MCP server."""

from typing import Any

from sqlalchemy import desc, func, select

from src.models.customer import Customer
from src.models.sales import Sale
from src.queries import CustomerQueryBuilder

from .base_tools import BaseTools


class CustomerTools(BaseTools):
	"""Tools for customer data analysis and querying."""

	async def get_top_customers(self, limit: int = 10) -> list:
		"""Get top customers by total purchase amount."""
		try:
			query = CustomerQueryBuilder.build_top_customers_query(limit)
			result = await self.db.execute(query)
			customers = result.fetchall()

			return [
				{
					"customer_id": customer.customer_id,
					"customer_name": customer.customer_name,
					"total_purchases": float(customer.total_purchases),
					"purchase_count": customer.purchase_count,
					"avg_purchase": float(customer.avg_purchase),
				}
				for customer in customers
			]
		except Exception:
			return []

	async def get_customer_details(self, customer_name: str) -> dict | None:
		"""Get detailed information about a specific customer."""
		try:
			customer_query = select(Customer).where(
				Customer.customer_name.ilike(f"%{customer_name}%")
			)
			customer_result = await self.db.execute(customer_query)
			customer = customer_result.scalar_one_or_none()

			if not customer:
				return None

			sales_query = (
				select(Sale)
				.where(Sale.customer_id == customer.id)
				.order_by(desc(Sale.sale_date))
			)
			sales_result = await self.db.execute(sales_query)
			sales = sales_result.scalars().all()

			total_spent = sum(float(sale.amount) for sale in sales)
			avg_purchase = total_spent / len(sales) if sales else 0

			return {
				"customer": self._format_customer_data(customer),
				"sales": [self._format_sale_data(sale) for sale in sales],
				"metrics": {
					"total_spent": total_spent,
					"purchase_count": len(sales),
					"avg_purchase": avg_purchase,
					"last_purchase": sales[0].sale_date.isoformat() if sales else None,
				},
			}
		except Exception:
			return None

	async def get_customers_summary(self) -> dict[str, Any]:
		"""Get overall customers summary."""
		try:
			query = select(
				func.count(Customer.id).label("total_customers"),
				func.count(Customer.id)
				.filter(Customer.is_active)
				.label("active_customers"),
				func.avg(Customer.credit_limit).label("avg_credit_limit"),
				func.sum(Customer.credit_limit).label("total_credit_limit"),
			)

			result = await self.db.execute(query)
			summary = result.fetchone()

			return {
				"total_customers": summary.total_customers,
				"active_customers": summary.active_customers,
				"avg_credit_limit": float(summary.avg_credit_limit or 0),
				"total_credit_limit": float(summary.total_credit_limit or 0),
			}
		except Exception as e:
			return {"error": f"Error getting customers summary: {str(e)}"}

	async def search_customers(
		self,
		search_term: str | None = None,
		customer_type: str | None = None,
		limit: int = 20,
	) -> list[dict[str, Any]]:
		"""Search customers by various criteria."""
		try:
			from sqlalchemy import or_

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

			return [self._format_customer_data(customer) for customer in customers]
		except Exception:
			return []

	async def get_customer_purchase_history(
		self, customer_id: int, limit: int = 50
	) -> dict[str, Any]:
		"""Get detailed purchase history for a customer."""
		try:
			customer_query = select(Customer).where(Customer.id == customer_id)
			customer_result = await self.db.execute(customer_query)
			customer = customer_result.scalar_one_or_none()

			if not customer:
				return {"error": "Customer not found"}

			sales_query = (
				select(Sale)
				.where(Sale.customer_id == customer_id)
				.order_by(desc(Sale.sale_date))
				.limit(limit)
			)
			sales_result = await self.db.execute(sales_query)
			sales = sales_result.scalars().all()

			total_spent = sum(float(sale.amount) for sale in sales)
			avg_purchase = total_spent / len(sales) if sales else 0

			monthly_data = {}
			for sale in sales:
				month_key = sale.sale_date.strftime("%Y-%m")
				if month_key not in monthly_data:
					monthly_data[month_key] = {"amount": 0, "count": 0}
				monthly_data[month_key]["amount"] += float(sale.amount)
				monthly_data[month_key]["count"] += 1

			return {
				"customer": self._format_customer_data(customer),
				"purchase_history": [self._format_sale_data(sale) for sale in sales],
				"metrics": {
					"total_spent": total_spent,
					"purchase_count": len(sales),
					"avg_purchase": avg_purchase,
					"first_purchase": sales[-1].sale_date.isoformat()
					if sales
					else None,
					"last_purchase": sales[0].sale_date.isoformat() if sales else None,
				},
				"monthly_breakdown": [
					{
						"month": month,
						"total_amount": data["amount"],
						"purchase_count": data["count"],
					}
					for month, data in sorted(monthly_data.items())
				],
			}
		except Exception as e:
			return {"error": f"Error getting purchase history: {str(e)}"}

	async def get_customers(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get customers with flexible filtering by any property."""
		try:
			query = CustomerQueryBuilder.build_customer_query(filters, order_by)
			query = CustomerQueryBuilder.apply_pagination(query, limit, offset)

			result = await self.db.execute(query)
			customers = result.scalars().all()

			count_query = CustomerQueryBuilder.build_customer_count_query(filters)
			count_result = await self.db.execute(count_query)
			total_count = count_result.scalar()

			customers_data = [
				self._format_customer_data(customer) for customer in customers
			]

			return {
				"customers": customers_data,
				"summary": {
					"total_count": total_count,
					"returned_count": len(customers_data),
					"active_count": sum(1 for c in customers if c.is_active),
					"total_credit_limit": sum(float(c.credit_limit) for c in customers),
				},
			}
		except Exception as e:
			return {
				"error": f"Error querying customers: {str(e)}",
				"error_type": type(e).__name__,
				"customers": [],
				"summary": {
					"total_count": 0,
					"returned_count": 0,
					"active_count": 0,
					"total_credit_limit": 0,
				},
			}
