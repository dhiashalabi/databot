"""Advanced analytics tools for MCP server."""

from datetime import datetime
from typing import Any

from sqlalchemy import desc, func, select

from src.models.invoice import Invoice
from src.models.product import Product
from src.models.sales import Sale

from .base_tools import BaseTools


class AnalyticsTools(BaseTools):
	"""Advanced analytics and reporting tools."""

	async def get_sales_trends(
		self, period: str = "month", limit: int = 12
	) -> dict[str, Any]:
		"""Get sales trends over time."""
		try:
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

			query = (
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

			result = await self.db.execute(query)
			trends = result.fetchall()

			trend_data = []
			for trend in trends:
				trend_data.append(
					{
						"period": trend.period.isoformat() if trend.period else None,
						"total_revenue": float(trend.total_revenue),
						"sales_count": trend.sales_count,
						"avg_sale": float(trend.avg_sale),
					}
				)

			return {
				"trends": trend_data,
				"period": period,
				"total_periods": len(trend_data),
			}
		except Exception as e:
			return {
				"error": f"Error getting sales trends: {str(e)}",
				"trends": [],
				"period": period,
				"total_periods": 0,
			}

	async def get_top_selling_products(
		self, limit: int = 10, start_date: str | None = None
	) -> dict[str, Any]:
		"""Get top selling products by revenue and quantity."""
		try:
			query = select(
				Sale.product_id,
				Sale.product_name,
				func.sum(Sale.amount).label("total_revenue"),
				func.sum(Sale.quantity).label("total_quantity"),
				func.count(Sale.id).label("sales_count"),
				func.avg(Sale.amount).label("avg_price"),
			).where(Sale.product_id.isnot(None))

			if start_date:
				start = datetime.fromisoformat(start_date)
				query = query.where(Sale.sale_date >= start)

			query = (
				query.group_by(Sale.product_id, Sale.product_name)
				.order_by(desc(func.sum(Sale.amount)))
				.limit(limit)
			)

			result = await self.db.execute(query)
			products = result.fetchall()

			product_data = []
			for product in products:
				product_data.append(
					{
						"product_id": product.product_id,
						"product_name": product.product_name,
						"total_revenue": float(product.total_revenue),
						"total_quantity": product.total_quantity,
						"sales_count": product.sales_count,
						"avg_price": float(product.avg_price),
					}
				)

			return {
				"products": product_data,
				"limit": limit,
				"total_products": len(product_data),
			}
		except Exception as e:
			return {
				"error": f"Error getting top products: {str(e)}",
				"products": [],
				"limit": limit,
				"total_products": 0,
			}

	async def get_sales_by_channel(
		self, start_date: str | None = None
	) -> dict[str, Any]:
		"""Get sales breakdown by channel."""
		try:
			query = (
				select(
					Sale.sales_channel,
					func.sum(Sale.amount).label("total_revenue"),
					func.count(Sale.id).label("sales_count"),
					func.avg(Sale.amount).label("avg_sale"),
				)
				.group_by(Sale.sales_channel)
				.order_by(desc(func.sum(Sale.amount)))
			)

			if start_date:
				start = datetime.fromisoformat(start_date)
				query = query.where(Sale.sale_date >= start)

			result = await self.db.execute(query)
			channels = result.fetchall()

			channel_data = []
			for channel in channels:
				channel_data.append(
					{
						"channel": channel.sales_channel,
						"total_revenue": float(channel.total_revenue),
						"sales_count": channel.sales_count,
						"avg_sale": float(channel.avg_sale),
					}
				)

			return {
				"channels": channel_data,
				"total_channels": len(channel_data),
			}
		except Exception as e:
			return {
				"error": f"Error getting sales by channel: {str(e)}",
				"channels": [],
				"total_channels": 0,
			}

	async def get_sales_forecast(
		self, periods: int = 6, period_type: str = "month"
	) -> dict[str, Any]:
		"""Generate sales forecast using simple linear regression."""
		try:
			if period_type == "month":
				date_trunc = func.date_trunc("month", Sale.sale_date)
			elif period_type == "week":
				date_trunc = func.date_trunc("week", Sale.sale_date)
			else:
				date_trunc = func.date_trunc("month", Sale.sale_date)

			query = (
				select(
					date_trunc.label("period"),
					func.sum(Sale.amount).label("revenue"),
				)
				.group_by(date_trunc)
				.order_by(date_trunc)
			)

			result = await self.db.execute(query)
			historical_data = result.fetchall()

			if len(historical_data) < 2:
				return {
					"error": "Insufficient historical data for forecasting",
					"forecast": [],
					"periods": periods,
				}

			periods_list = list(range(len(historical_data)))
			revenues = [float(data.revenue) for data in historical_data]

			n = len(periods_list)
			sum_x = sum(periods_list)
			sum_y = sum(revenues)
			sum_xy = sum(x * y for x, y in zip(periods_list, revenues, strict=True))
			sum_x2 = sum(x * x for x in periods_list)

			slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
			intercept = (sum_y - slope * sum_x) / n

			forecast = []
			last_period = len(historical_data)
			for i in range(periods):
				period_num = last_period + i
				predicted_revenue = slope * period_num + intercept
				forecast.append(
					{
						"period": period_num,
						"predicted_revenue": max(0, predicted_revenue),
					}
				)

			return {
				"forecast": forecast,
				"periods": periods,
				"period_type": period_type,
				"historical_data_points": len(historical_data),
			}
		except Exception as e:
			return {
				"error": f"Error generating forecast: {str(e)}",
				"forecast": [],
				"periods": periods,
			}

	async def get_customer_segmentation(self) -> dict[str, Any]:
		"""Perform RFM analysis for customer segmentation."""
		try:
			query = (
				select(
					Sale.customer_id,
					Sale.customer_name,
					func.max(Sale.sale_date).label("last_purchase"),
					func.count(Sale.id).label("frequency"),
					func.sum(Sale.amount).label("monetary"),
				)
				.where(Sale.customer_id.isnot(None))
				.group_by(Sale.customer_id, Sale.customer_name)
			)

			result = await self.db.execute(query)
			customers = result.fetchall()

			if not customers:
				return {"error": "No customer data found"}

			now = datetime.now()
			rfm_data = []

			for customer in customers:
				recency = (now - customer.last_purchase).days
				frequency = customer.frequency
				monetary = float(customer.monetary)

				rfm_data.append(
					{
						"customer_id": customer.customer_id,
						"customer_name": customer.customer_name,
						"recency": recency,
						"frequency": frequency,
						"monetary": monetary,
					}
				)

			recency_values = [c["recency"] for c in rfm_data]
			frequency_values = [c["frequency"] for c in rfm_data]
			monetary_values = [c["monetary"] for c in rfm_data]

			recency_q1 = sorted(recency_values)[len(recency_values) // 4]
			frequency_q3 = sorted(frequency_values)[3 * len(frequency_values) // 4]
			monetary_q3 = sorted(monetary_values)[3 * len(monetary_values) // 4]

			segments = {
				"champions": 0,
				"loyal_customers": 0,
				"potential_loyalists": 0,
				"at_risk": 0,
				"lost": 0,
			}

			for customer in rfm_data:
				if (
					customer["recency"] <= recency_q1
					and customer["frequency"] >= frequency_q3
					and customer["monetary"] >= monetary_q3
				):
					customer["segment"] = "champions"
					segments["champions"] += 1
				elif (
					customer["recency"] <= recency_q1
					and customer["frequency"] >= frequency_q3
				):
					customer["segment"] = "loyal_customers"
					segments["loyal_customers"] += 1
				elif customer["recency"] <= recency_q1:
					customer["segment"] = "potential_loyalists"
					segments["potential_loyalists"] += 1
				elif customer["recency"] > recency_q1 * 2:
					customer["segment"] = "lost"
					segments["lost"] += 1
				else:
					customer["segment"] = "at_risk"
					segments["at_risk"] += 1

			return {
				"segmentation": rfm_data,
				"segment_counts": segments,
				"total_customers": len(rfm_data),
			}
		except Exception as e:
			return {
				"error": f"Error performing customer segmentation: {str(e)}",
				"segmentation": [],
				"segment_counts": {},
				"total_customers": 0,
			}

	async def get_customer_lifetime_value(
		self, customer_id: int | None = None
	) -> dict[str, Any]:
		"""Calculate customer lifetime value."""
		try:
			if customer_id:
				query = (
					select(
						Sale.customer_id,
						Sale.customer_name,
						func.sum(Sale.amount).label("total_value"),
						func.count(Sale.id).label("total_orders"),
						func.avg(Sale.amount).label("avg_order_value"),
						func.min(Sale.sale_date).label("first_purchase"),
						func.max(Sale.sale_date).label("last_purchase"),
					)
					.where(Sale.customer_id == customer_id)
					.group_by(Sale.customer_id, Sale.customer_name)
				)
			else:
				query = (
					select(
						Sale.customer_id,
						Sale.customer_name,
						func.sum(Sale.amount).label("total_value"),
						func.count(Sale.id).label("total_orders"),
						func.avg(Sale.amount).label("avg_order_value"),
						func.min(Sale.sale_date).label("first_purchase"),
						func.max(Sale.sale_date).label("last_purchase"),
					)
					.where(Sale.customer_id.isnot(None))
					.group_by(Sale.customer_id, Sale.customer_name)
					.order_by(desc(func.sum(Sale.amount)))
				)

			result = await self.db.execute(query)
			customers = result.fetchall()

			clv_data = []
			for customer in customers:
				lifespan_days = (customer.last_purchase - customer.first_purchase).days
				lifespan_months = lifespan_days / 30.44 if lifespan_days > 0 else 1

				monthly_value = (
					float(customer.total_value) / lifespan_months
					if lifespan_months > 0
					else 0
				)
				clv = monthly_value * 12

				clv_data.append(
					{
						"customer_id": customer.customer_id,
						"customer_name": customer.customer_name,
						"total_value": float(customer.total_value),
						"total_orders": customer.total_orders,
						"avg_order_value": float(customer.avg_order_value),
						"first_purchase": customer.first_purchase.isoformat(),
						"last_purchase": customer.last_purchase.isoformat(),
						"lifespan_days": lifespan_days,
						"monthly_value": monthly_value,
						"clv": clv,
					}
				)

			return {
				"clv_data": clv_data,
				"total_customers": len(clv_data),
			}
		except Exception as e:
			return {
				"error": f"Error calculating CLV: {str(e)}",
				"clv_data": [],
				"total_customers": 0,
			}

	async def get_product_performance_analysis(
		self, product_id: int | None = None
	) -> dict[str, Any]:
		"""Analyze product performance metrics."""
		try:
			if product_id:
				query = (
					select(
						Sale.product_id,
						Sale.product_name,
						func.sum(Sale.amount).label("total_revenue"),
						func.sum(Sale.quantity).label("total_quantity"),
						func.count(Sale.id).label("sales_count"),
						func.avg(Sale.amount).label("avg_price"),
						func.min(Sale.sale_date).label("first_sale"),
						func.max(Sale.sale_date).label("last_sale"),
					)
					.where(Sale.product_id == product_id)
					.group_by(Sale.product_id, Sale.product_name)
				)
			else:
				query = (
					select(
						Sale.product_id,
						Sale.product_name,
						func.sum(Sale.amount).label("total_revenue"),
						func.sum(Sale.quantity).label("total_quantity"),
						func.count(Sale.id).label("sales_count"),
						func.avg(Sale.amount).label("avg_price"),
						func.min(Sale.sale_date).label("first_sale"),
						func.max(Sale.sale_date).label("last_sale"),
					)
					.where(Sale.product_id.isnot(None))
					.group_by(Sale.product_id, Sale.product_name)
					.order_by(desc(func.sum(Sale.amount)))
				)

			result = await self.db.execute(query)
			products = result.fetchall()

			performance_data = []
			for product in products:
				days_active = (
					(product.last_sale - product.first_sale).days
					if product.first_sale and product.last_sale
					else 0
				)
				daily_avg_sales = (
					float(product.total_revenue) / days_active if days_active > 0 else 0
				)

				performance_data.append(
					{
						"product_id": product.product_id,
						"product_name": product.product_name,
						"total_revenue": float(product.total_revenue),
						"total_quantity": product.total_quantity,
						"sales_count": product.sales_count,
						"avg_price": float(product.avg_price),
						"first_sale": product.first_sale.isoformat()
						if product.first_sale
						else None,
						"last_sale": product.last_sale.isoformat()
						if product.last_sale
						else None,
						"days_active": days_active,
						"daily_avg_sales": daily_avg_sales,
					}
				)

			return {
				"performance_data": performance_data,
				"total_products": len(performance_data),
			}
		except Exception as e:
			return {
				"error": f"Error analyzing product performance: {str(e)}",
				"performance_data": [],
				"total_products": 0,
			}

	async def get_inventory_analysis(self) -> dict[str, Any]:
		"""Analyze inventory levels and turnover."""
		try:
			query = select(Product)

			result = await self.db.execute(query)
			products = result.scalars().all()

			inventory_data = []
			total_value = 0
			low_stock_count = 0
			out_of_stock_count = 0

			for product in products:
				cost_price = product.cost_price or product.unit_price
				inventory_value = float(product.stock_quantity * cost_price)
				total_value += inventory_value

				stock_status = "in_stock"
				if product.stock_quantity == 0:
					stock_status = "out_of_stock"
					out_of_stock_count += 1
				elif product.stock_quantity <= product.reorder_level:
					stock_status = "low_stock"
					low_stock_count += 1

				inventory_data.append(
					{
						"product_id": product.id,
						"product_name": product.product_name,
						"sku": product.sku,
						"stock_quantity": product.stock_quantity,
						"reorder_level": product.reorder_level,
						"unit_price": float(product.unit_price),
						"cost_price": float(cost_price),
						"inventory_value": inventory_value,
						"stock_status": stock_status,
						"is_active": product.is_active,
					}
				)

			return {
				"inventory_data": inventory_data,
				"summary": {
					"total_products": len(products),
					"total_inventory_value": total_value,
					"low_stock_count": low_stock_count,
					"out_of_stock_count": out_of_stock_count,
					"in_stock_count": len(products)
					- low_stock_count
					- out_of_stock_count,
				},
			}
		except Exception as e:
			return {
				"error": f"Error analyzing inventory: {str(e)}",
				"inventory_data": [],
				"summary": {
					"total_products": 0,
					"total_inventory_value": 0,
					"low_stock_count": 0,
					"out_of_stock_count": 0,
					"in_stock_count": 0,
				},
			}

	async def get_category_performance(self) -> dict[str, Any]:
		"""Analyze performance by product category."""
		try:
			query = (
				select(
					Sale.category,
					func.sum(Sale.amount).label("total_revenue"),
					func.sum(Sale.quantity).label("total_quantity"),
					func.count(Sale.id).label("sales_count"),
					func.avg(Sale.amount).label("avg_sale"),
				)
				.where(Sale.category.isnot(None))
				.group_by(Sale.category)
				.order_by(desc(func.sum(Sale.amount)))
			)

			result = await self.db.execute(query)
			categories = result.fetchall()

			category_data = []
			for category in categories:
				category_data.append(
					{
						"category": category.category,
						"total_revenue": float(category.total_revenue),
						"total_quantity": category.total_quantity,
						"sales_count": category.sales_count,
						"avg_sale": float(category.avg_sale),
					}
				)

			return {
				"category_data": category_data,
				"total_categories": len(category_data),
			}
		except Exception as e:
			return {
				"error": f"Error analyzing category performance: {str(e)}",
				"category_data": [],
				"total_categories": 0,
			}

	async def get_invoice_analysis(self) -> dict[str, Any]:
		"""Analyze invoice patterns and payment behavior."""
		try:
			query = select(Invoice)

			result = await self.db.execute(query)
			invoices = result.scalars().all()

			if not invoices:
				return {"error": "No invoice data found"}

			total_invoices = len(invoices)
			paid_invoices = sum(1 for i in invoices if i.status == "paid")
			pending_invoices = sum(1 for i in invoices if i.status == "pending")

			total_amount = sum(float(i.total_amount) for i in invoices)
			paid_amount = sum(
				float(i.total_amount) for i in invoices if i.status == "paid"
			)
			pending_amount = sum(
				float(i.total_amount) for i in invoices if i.status == "pending"
			)

			paid_invoices_with_dates = [
				i
				for i in invoices
				if i.status == "paid" and i.invoice_date and i.updated_at
			]
			avg_days_to_payment = 0
			if paid_invoices_with_dates:
				days_list = [
					(i.updated_at - i.invoice_date).days
					for i in paid_invoices_with_dates
				]
				avg_days_to_payment = sum(days_list) / len(days_list)

			return {
				"summary": {
					"total_invoices": total_invoices,
					"paid_invoices": paid_invoices,
					"pending_invoices": pending_invoices,
					"total_amount": total_amount,
					"paid_amount": paid_amount,
					"pending_amount": pending_amount,
					"payment_rate": (paid_invoices / total_invoices * 100)
					if total_invoices > 0
					else 0,
					"avg_days_to_payment": avg_days_to_payment,
				},
				"invoices": [
					self._format_invoice_data(invoice) for invoice in invoices
				],
			}
		except Exception as e:
			return {
				"error": f"Error analyzing invoices: {str(e)}",
				"summary": {
					"total_invoices": 0,
					"paid_invoices": 0,
					"pending_invoices": 0,
					"total_amount": 0,
					"paid_amount": 0,
					"pending_amount": 0,
					"payment_rate": 0,
					"avg_days_to_payment": 0,
				},
				"invoices": [],
			}

	async def get_revenue_analysis(
		self, start_date: str | None = None, end_date: str | None = None
	) -> dict[str, Any]:
		"""Comprehensive revenue analysis."""
		try:
			query = select(Sale)

			if start_date:
				start = datetime.fromisoformat(start_date)
				query = query.where(Sale.sale_date >= start)

			if end_date:
				end = datetime.fromisoformat(end_date)
				query = query.where(Sale.sale_date <= end)

			result = await self.db.execute(query)
			sales = result.scalars().all()

			if not sales:
				return {"error": "No sales data found for the specified period"}

			total_revenue = sum(float(sale.amount) for sale in sales)
			total_quantity = sum(sale.quantity for sale in sales)
			avg_sale = total_revenue / len(sales) if sales else 0

			category_revenue = {}
			for sale in sales:
				category = sale.category or "Unknown"
				if category not in category_revenue:
					category_revenue[category] = {
						"revenue": 0,
						"quantity": 0,
						"count": 0,
					}
				category_revenue[category]["revenue"] += float(sale.amount)
				category_revenue[category]["quantity"] += sale.quantity
				category_revenue[category]["count"] += 1

			channel_revenue = {}
			for sale in sales:
				channel = sale.sales_channel or "Unknown"
				if channel not in channel_revenue:
					channel_revenue[channel] = {"revenue": 0, "quantity": 0, "count": 0}
				channel_revenue[channel]["revenue"] += float(sale.amount)
				channel_revenue[channel]["quantity"] += sale.quantity
				channel_revenue[channel]["count"] += 1

			return {
				"summary": {
					"total_revenue": total_revenue,
					"total_quantity": total_quantity,
					"total_sales": len(sales),
					"avg_sale": avg_sale,
					"period": {
						"start_date": start_date,
						"end_date": end_date,
					},
				},
				"category_breakdown": [
					{
						"category": category,
						"revenue": data["revenue"],
						"quantity": data["quantity"],
						"count": data["count"],
						"percentage": (data["revenue"] / total_revenue * 100)
						if total_revenue > 0
						else 0,
					}
					for category, data in category_revenue.items()
				],
				"channel_breakdown": [
					{
						"channel": channel,
						"revenue": data["revenue"],
						"quantity": data["quantity"],
						"count": data["count"],
						"percentage": (data["revenue"] / total_revenue * 100)
						if total_revenue > 0
						else 0,
					}
					for channel, data in channel_revenue.items()
				],
			}
		except Exception as e:
			return {
				"error": f"Error analyzing revenue: {str(e)}",
				"summary": {
					"total_revenue": 0,
					"total_quantity": 0,
					"total_sales": 0,
					"avg_sale": 0,
				},
				"category_breakdown": [],
				"channel_breakdown": [],
			}
