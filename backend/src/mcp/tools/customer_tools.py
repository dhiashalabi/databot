"""Customer-related tools for MCP server."""

from typing import Any

from sqlalchemy import desc, func, select

from src.models.customer import Customer
from src.models.sales import Sale
from src.queries import CustomerQueryBuilder
from src.utils.fuzzy_search import find_fuzzy_matches, sanitize_search_term

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
		"""Get detailed information about a specific customer with fuzzy matching fallback."""
		try:
			sanitized_name = sanitize_search_term(customer_name)
			if not sanitized_name:
				return None

			customer_query = CustomerQueryBuilder.build_customer_details_query(
				sanitized_name
			)
			customer_result = await self.db.execute(customer_query)
			customer = customer_result.scalar_one_or_none()

			if not customer:
				fuzzy_result = await self._fuzzy_search_customers(
					sanitized_name, threshold=0.5, limit=1
				)

				if fuzzy_result.get("customers"):
					best_match = fuzzy_result["customers"][0]
					customer_id = best_match["id"]
					customer_query = select(Customer).where(Customer.id == customer_id)
					customer_result = await self.db.execute(customer_query)
					customer = customer_result.scalar_one_or_none()

					if customer:
						fuzzy_info = {
							"fuzzy_match": True,
							"original_search": customer_name,
							"matched_name": customer.customer_name,
							"similarity_score": best_match["similarity_score"],
						}
					else:
						return None
				else:
					return None
			else:
				fuzzy_info = {"fuzzy_match": False}

			sales_query = (
				select(Sale)
				.where(Sale.customer_id == customer.id)
				.order_by(desc(Sale.sale_date))
			)
			sales_result = await self.db.execute(sales_query)
			sales = sales_result.scalars().all()

			total_spent = sum(float(sale.amount) for sale in sales)
			avg_purchase = total_spent / len(sales) if sales else 0

			result = {
				"customer": self._format_customer_data(customer),
				"sales": [self._format_sale_data(sale) for sale in sales],
				"metrics": {
					"total_spent": total_spent,
					"purchase_count": len(sales),
					"avg_purchase": avg_purchase,
					"last_purchase": sales[0].sale_date.isoformat() if sales else None,
				},
			}

			if fuzzy_info.get("fuzzy_match"):
				result["fuzzy_info"] = fuzzy_info

			return result
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
		"""Search customers by various criteria with fuzzy matching fallback."""
		try:
			if search_term:
				sanitized_term = sanitize_search_term(search_term)
				if not sanitized_term:
					return []

				query = CustomerQueryBuilder.build_customer_search_query(
					sanitized_term, limit
				)
			else:
				query = select(Customer).limit(limit).order_by(Customer.customer_name)

			if customer_type:
				query = query.where(Customer.customer_type == customer_type)

			result = await self.db.execute(query)
			customers = result.scalars().all()

			if not customers and search_term:
				fuzzy_result = await self._fuzzy_search_customers(
					sanitized_term, threshold=0.5, limit=limit
				)
				return fuzzy_result.get("customers", [])

			return [self._format_customer_data(customer) for customer in customers]
		except Exception:
			return []

	async def _fuzzy_search_customers(
		self,
		search_term: str,
		threshold: float = 0.5,
		limit: int = 10,
	) -> dict[str, Any]:
		"""Internal fuzzy search method with ILIKE pre-filtering for efficiency."""
		try:
			sanitized_term = sanitize_search_term(search_term)
			if not sanitized_term:
				return {"customers": []}

			candidates_query = CustomerQueryBuilder.build_fuzzy_search_candidates_query(
				sanitized_term, limit=50
			)

			result = await self.db.execute(candidates_query)
			candidate_customers = result.fetchall()

			if not candidate_customers:
				return {"customers": []}

			customer_names = [
				customer.customer_name for customer in candidate_customers
			]

			fuzzy_matches = find_fuzzy_matches(
				sanitized_term, customer_names, threshold
			)

			if not fuzzy_matches:
				return {"customers": []}

			matched_names = [match[0] for match in fuzzy_matches[:limit]]
			customers_query = select(Customer).where(
				Customer.customer_name.in_(matched_names)
			)
			customers_result = await self.db.execute(customers_query)
			customers = customers_result.scalars().all()

			customers_data = []
			for customer in customers:
				customer_data = self._format_customer_data(customer)
				similarity = next(
					(
						score
						for name, score in fuzzy_matches
						if name == customer.customer_name
					),
					0.0,
				)
				customer_data["similarity_score"] = round(similarity, 3)
				customers_data.append(customer_data)

			customers_data.sort(key=lambda x: x["similarity_score"], reverse=True)

			return {"customers": customers_data}

		except Exception:
			return {"customers": []}

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

			sales_query = CustomerQueryBuilder.build_customer_purchase_history_query(
				customer_id, limit
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
