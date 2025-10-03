"""AI-Powered Insights Engine for advanced business analytics."""

from datetime import datetime, timedelta
import statistics
from typing import Any

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.customer import Customer
from src.models.product import Product
from src.models.sales import Sale


class AIInsightsEngine:
	"""AI-powered insights engine for advanced business analytics."""

	def __init__(self, db: AsyncSession):
		"""Initialize with database session."""
		self.db = db

	async def get_sales_analytics(
		self,
		start_date: str,
		end_date: str,
		category: str | None = None,
		include_insights: bool = True,
	) -> dict[str, Any]:
		"""Get comprehensive sales analytics with AI-powered insights."""
		start_dt = datetime.strptime(start_date, "%Y-%m-%d")
		end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
			hour=23, minute=59, second=59
		)

		base_query = select(
			func.sum(Sale.amount).label("total_amount"),
			func.sum(Sale.quantity).label("total_quantity"),
			func.count(Sale.id).label("transaction_count"),
			func.avg(Sale.amount).label("avg_transaction_value"),
			func.max(Sale.amount).label("max_transaction"),
			func.min(Sale.amount).label("min_transaction"),
		).where(and_(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt))

		if category:
			base_query = base_query.where(Sale.category == category)

		result = await self.db.execute(base_query)
		sales_data = result.first()

		daily_query = select(
			func.date(Sale.sale_date).label("date"),
			func.sum(Sale.amount).label("daily_amount"),
			func.sum(Sale.quantity).label("daily_quantity"),
			func.count(Sale.id).label("daily_transactions"),
		).where(and_(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt))

		if category:
			daily_query = daily_query.where(Sale.category == category)

		daily_query = daily_query.group_by(func.date(Sale.sale_date)).order_by(
			func.date(Sale.sale_date)
		)
		daily_result = await self.db.execute(daily_query)
		daily_data = [dict(row._mapping) for row in daily_result]

		category_query = (
			select(
				Sale.category,
				func.sum(Sale.amount).label("category_amount"),
				func.sum(Sale.quantity).label("category_quantity"),
				func.count(Sale.id).label("category_transactions"),
			)
			.where(and_(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt))
			.group_by(Sale.category)
			.order_by(desc("category_amount"))
		)

		category_result = await self.db.execute(category_query)
		category_data = [dict(row._mapping) for row in category_result]

		product_query = (
			select(
				Sale.product_name,
				func.sum(Sale.amount).label("product_amount"),
				func.sum(Sale.quantity).label("product_quantity"),
				func.count(Sale.id).label("product_transactions"),
			)
			.where(and_(Sale.sale_date >= start_dt, Sale.sale_date <= end_dt))
			.group_by(Sale.product_name)
			.order_by(desc("product_amount"))
			.limit(10)
		)

		product_result = await self.db.execute(product_query)
		top_products = [dict(row._mapping) for row in product_result]

		analytics = {
			"period": {"start": start_date, "end": end_date},
			"summary": {
				"total_revenue": float(sales_data.total_amount or 0),
				"total_quantity": int(sales_data.total_quantity or 0),
				"transaction_count": int(sales_data.transaction_count or 0),
				"avg_transaction_value": float(sales_data.avg_transaction_value or 0),
				"max_transaction": float(sales_data.max_transaction or 0),
				"min_transaction": float(sales_data.min_transaction or 0),
			},
			"daily_breakdown": daily_data,
			"category_breakdown": category_data,
			"top_products": top_products,
		}

		if include_insights:
			analytics["ai_insights"] = await self._generate_sales_insights(analytics)

		return analytics

	async def get_customer_insights(
		self,
		customer_id: str | None = None,
		timeframe: str = "30d",
		include_predictions: bool = True,
	) -> dict[str, Any]:
		"""Get AI-powered customer behavior insights and segmentation."""
		end_date = datetime.now()
		if timeframe == "7d":
			start_date = end_date - timedelta(days=7)
		elif timeframe == "30d":
			start_date = end_date - timedelta(days=30)
		elif timeframe == "90d":
			start_date = end_date - timedelta(days=90)
		elif timeframe == "1y":
			start_date = end_date - timedelta(days=365)
		else:
			start_date = end_date - timedelta(days=30)

		if customer_id:
			customer_query = select(Customer).where(Customer.id == int(customer_id))
			customer_result = await self.db.execute(customer_query)
			customer = customer_result.scalar_one_or_none()
			if not customer:
				return {"error": "Customer not found"}

			sales_query = select(
				func.sum(Sale.amount).label("total_spent"),
				func.count(Sale.id).label("total_orders"),
				func.avg(Sale.amount).label("avg_order_value"),
				func.max(Sale.sale_date).label("last_purchase"),
			).where(
				and_(Sale.customer_id == int(customer_id), Sale.sale_date >= start_date)
			)

			sales_result = await self.db.execute(sales_query)
			sales_data = sales_result.first()

			customer_insights = {
				"customer_info": {
					"id": customer.id,
					"name": customer.customer_name,
					"email": customer.email,
					"phone": customer.phone,
					"address": customer.address,
				},
				"purchase_behavior": {
					"total_spent": float(sales_data.total_spent or 0),
					"total_orders": int(sales_data.total_orders or 0),
					"avg_order_value": float(sales_data.avg_order_value or 0),
					"last_purchase": sales_data.last_purchase.isoformat()
					if sales_data.last_purchase
					else None,
				},
			}

			if include_predictions:
				customer_insights[
					"predictions"
				] = await self._predict_customer_behavior(customer_id, sales_data)

			return customer_insights

		else:
			customers_query = (
				select(
					Customer.id,
					Customer.customer_name,
					Customer.email,
					func.sum(Sale.amount).label("total_spent"),
					func.count(Sale.id).label("total_orders"),
					func.avg(Sale.amount).label("avg_order_value"),
					func.max(Sale.sale_date).label("last_purchase"),
				)
				.select_from(Customer)
				.join(Sale, Customer.id == Sale.customer_id, isouter=True)
				.where(or_(Sale.sale_date >= start_date, Sale.sale_date.is_(None)))
				.group_by(Customer.id, Customer.customer_name, Customer.email)
			)

			customers_result = await self.db.execute(customers_query)
			customers_data = [dict(row._mapping) for row in customers_result]

			segmentation = await self._segment_customers(customers_data)

			insights = {
				"timeframe": timeframe,
				"total_customers": len(customers_data),
				"customer_data": customers_data,
				"segmentation": segmentation,
			}

			if include_predictions:
				insights["predictions"] = await self._predict_customer_trends(
					customers_data
				)

			return insights

	async def get_product_performance(
		self,
		product_id: str | None = None,
		period: str = "month",
		include_recommendations: bool = True,
	) -> dict[str, Any]:
		"""Analyze product performance with trend analysis and recommendations."""
		end_date = datetime.now()
		if period == "week":
			start_date = end_date - timedelta(weeks=1)
		elif period == "month":
			start_date = end_date - timedelta(days=30)
		elif period == "quarter":
			start_date = end_date - timedelta(days=90)
		elif period == "year":
			start_date = end_date - timedelta(days=365)
		else:
			start_date = end_date - timedelta(days=30)

		if product_id:
			product_query = select(Product).where(Product.id == int(product_id))
			product_result = await self.db.execute(product_query)
			product = product_result.scalar_one_or_none()

			if not product:
				return {"error": "Product not found"}

			sales_query = select(
				func.sum(Sale.amount).label("total_revenue"),
				func.sum(Sale.quantity).label("total_quantity"),
				func.count(Sale.id).label("total_sales"),
				func.avg(Sale.amount).label("avg_sale_price"),
				func.max(Sale.sale_date).label("last_sale"),
			).where(
				and_(Sale.product_id == int(product_id), Sale.sale_date >= start_date)
			)

			sales_result = await self.db.execute(sales_query)
			sales_data = sales_result.first()

			daily_query = (
				select(
					func.date(Sale.sale_date).label("date"),
					func.sum(Sale.amount).label("daily_revenue"),
					func.sum(Sale.quantity).label("daily_quantity"),
				)
				.where(
					and_(
						Sale.product_id == int(product_id), Sale.sale_date >= start_date
					)
				)
				.group_by(func.date(Sale.sale_date))
				.order_by(func.date(Sale.sale_date))
			)

			daily_result = await self.db.execute(daily_query)
			daily_data = [dict(row._mapping) for row in daily_result]

			performance = {
				"product_info": {
					"id": product.id,
					"name": product.product_name,
					"category_id": product.category_id,
					"unit_price": float(product.unit_price),
					"is_active": product.is_active,
				},
				"performance": {
					"total_revenue": float(sales_data.total_revenue or 0),
					"total_quantity": int(sales_data.total_quantity or 0),
					"total_sales": int(sales_data.total_sales or 0),
					"avg_sale_price": float(sales_data.avg_sale_price or 0),
					"last_sale": sales_data.last_sale.isoformat()
					if sales_data.last_sale
					else None,
				},
				"daily_performance": daily_data,
			}

			if include_recommendations:
				performance[
					"recommendations"
				] = await self._generate_product_recommendations(
					product, sales_data, daily_data
				)

			return performance

		else:
			products_query = (
				select(
				Product.id,
				Product.product_name,
				Product.category_id,
				Product.unit_price,
					func.sum(Sale.amount).label("total_revenue"),
					func.sum(Sale.quantity).label("total_quantity"),
					func.count(Sale.id).label("total_sales"),
				)
				.select_from(Product)
				.join(Sale, Product.id == Sale.product_id, isouter=True)
				.where(
					and_(
						or_(Sale.sale_date >= start_date, Sale.sale_date.is_(None)),
						Product.is_active,
					)
				)
				.group_by(
					Product.id, Product.product_name, Product.category_id, Product.unit_price
				)
				.order_by(desc("total_revenue"))
			)

			products_result = await self.db.execute(products_query)
			products_data = [dict(row._mapping) for row in products_result]

			category_query = (
				select(
					Product.category_id,
					func.sum(Sale.amount).label("category_revenue"),
					func.sum(Sale.quantity).label("category_quantity"),
					func.count(Sale.id).label("category_sales"),
				)
				.select_from(Product)
				.join(Sale, Product.id == Sale.product_id, isouter=True)
				.where(
					and_(
						or_(Sale.sale_date >= start_date, Sale.sale_date.is_(None)),
						Product.is_active,
					)
				)
				.group_by(Product.category_id)
				.order_by(desc("category_revenue"))
			)

			category_result = await self.db.execute(category_query)
			category_data = [dict(row._mapping) for row in category_result]

			performance = {
				"period": period,
				"total_products": len(products_data),
				"products_data": products_data,
				"category_performance": category_data,
			}

			if include_recommendations:
				performance[
					"recommendations"
				] = await self._generate_portfolio_recommendations(
					products_data, category_data
				)

			return performance

	async def get_business_insights(
		self, insight_type: str, timeframe: str = "30d"
	) -> dict[str, Any]:
		"""Get comprehensive business insights with AI analysis."""
		end_date = datetime.now()
		if timeframe == "7d":
			start_date = end_date - timedelta(days=7)
		elif timeframe == "30d":
			start_date = end_date - timedelta(days=30)
		elif timeframe == "90d":
			start_date = end_date - timedelta(days=90)
		elif timeframe == "1y":
			start_date = end_date - timedelta(days=365)
		else:
			start_date = end_date - timedelta(days=30)

		if insight_type == "overview":
			return await self._get_business_overview(start_date, end_date)
		elif insight_type == "trends":
			return await self._analyze_business_trends(start_date, end_date)
		elif insight_type == "anomalies":
			return await self._detect_anomalies(start_date, end_date)
		elif insight_type == "forecast":
			return await self._generate_forecast(start_date, end_date)
		else:
			return {"error": f"Unknown insight type: {insight_type}"}

	async def compare_periods(
		self,
		period1_start: str,
		period1_end: str,
		period2_start: str,
		period2_end: str,
		metrics: list[str] = None,
	) -> dict[str, Any]:
		"""Compare business metrics between two periods with AI analysis."""
		if metrics is None:
			metrics = ["sales", "customers", "products"]

		p1_start = datetime.strptime(period1_start, "%Y-%m-%d")
		p1_end = datetime.strptime(period1_end, "%Y-%m-%d").replace(
			hour=23, minute=59, second=59
		)
		p2_start = datetime.strptime(period2_start, "%Y-%m-%d")
		p2_end = datetime.strptime(period2_end, "%Y-%m-%d").replace(
			hour=23, minute=59, second=59
		)

		comparison = {
			"period1": {"start": period1_start, "end": period1_end},
			"period2": {"start": period2_start, "end": period2_end},
			"metrics": {},
		}

		for metric in metrics:
			if metric == "sales":
				p1_sales = await self._get_sales_metrics(p1_start, p1_end)
				p2_sales = await self._get_sales_metrics(p2_start, p2_end)
				comparison["metrics"]["sales"] = {
					"period1": p1_sales,
					"period2": p2_sales,
					"change": self._calculate_change(p1_sales, p2_sales),
				}
			elif metric == "customers":
				p1_customers = await self._get_customer_metrics(p1_start, p1_end)
				p2_customers = await self._get_customer_metrics(p2_start, p2_end)
				comparison["metrics"]["customers"] = {
					"period1": p1_customers,
					"period2": p2_customers,
					"change": self._calculate_change(p1_customers, p2_customers),
				}
			elif metric == "products":
				p1_products = await self._get_product_metrics(p1_start, p1_end)
				p2_products = await self._get_product_metrics(p2_start, p2_end)
				comparison["metrics"]["products"] = {
					"period1": p1_products,
					"period2": p2_products,
					"change": self._calculate_change(p1_products, p2_products),
				}

		comparison["ai_analysis"] = await self._analyze_period_comparison(comparison)

		return comparison

	async def _generate_sales_insights(
		self, analytics: dict[str, Any]
	) -> dict[str, Any]:
		"""Generate AI-powered sales insights."""
		insights = {
			"trends": [],
			"opportunities": [],
			"risks": [],
			"recommendations": [],
		}

		daily_amounts = [day["daily_amount"] for day in analytics["daily_breakdown"]]
		if len(daily_amounts) > 1:
			trend = (
				"increasing" if daily_amounts[-1] > daily_amounts[0] else "decreasing"
			)
			insights["trends"].append(f"Sales trend is {trend} over the period")

		if analytics["category_breakdown"]:
			top_category = analytics["category_breakdown"][0]
			insights["opportunities"].append(
				f"Focus on {top_category['category']} category - highest revenue generator"
			)

		avg_value = analytics["summary"]["avg_transaction_value"]
		if avg_value > 100:
			insights["recommendations"].append(
				"High average transaction value - consider upselling strategies"
			)
		elif avg_value < 50:
			insights["recommendations"].append(
				"Low average transaction value - consider bundling strategies"
			)

		return insights

	async def _predict_customer_behavior(
		self, customer_id: str, sales_data: Any
	) -> dict[str, Any]:
		"""Predict customer behavior using simple heuristics."""
		predictions = {
			"churn_risk": "low",
			"next_purchase_likelihood": "high",
			"recommended_actions": [],
		}

		if sales_data.last_purchase:
			days_since_last = (datetime.now() - sales_data.last_purchase).days
			if days_since_last > 90:
				predictions["churn_risk"] = "high"
				predictions["recommended_actions"].append("Send re-engagement campaign")
			elif days_since_last > 30:
				predictions["churn_risk"] = "medium"
				predictions["recommended_actions"].append("Send promotional offer")

		if sales_data.total_orders < 2:
			predictions["next_purchase_likelihood"] = "medium"
			predictions["recommended_actions"].append("Focus on customer retention")

		return predictions

	async def _segment_customers(
		self, customers_data: list[dict[str, Any]]
	) -> dict[str, Any]:
		"""Segment customers based on their behavior."""
		segments = {
			"high_value": [],
			"medium_value": [],
			"low_value": [],
			"at_risk": [],
		}

		total_spent_values = [c["total_spent"] or 0 for c in customers_data]
		if total_spent_values:
			avg_spent = statistics.mean(total_spent_values)
			high_threshold = avg_spent * 1.5
			low_threshold = avg_spent * 0.5

		for customer in customers_data:
			total_spent = customer["total_spent"] or 0
			last_purchase = customer["last_purchase"]

			if last_purchase:
				days_since_last = (datetime.now() - last_purchase).days
				if days_since_last > 60:
					segments["at_risk"].append(customer)
				elif total_spent >= high_threshold:
					segments["high_value"].append(customer)
				elif total_spent >= low_threshold:
					segments["medium_value"].append(customer)
				else:
					segments["low_value"].append(customer)
			else:
				segments["low_value"].append(customer)

		return segments

	async def _generate_product_recommendations(
		self, product: Any, sales_data: Any, daily_data: list[dict[str, Any]]
	) -> list[str]:
		"""Generate product-specific recommendations."""
		recommendations = []

		if sales_data.total_quantity == 0:
			recommendations.append(
				"Product has no sales - consider promotional pricing"
			)
		elif sales_data.total_quantity < 10:
			recommendations.append("Low sales volume - consider marketing campaigns")

		if daily_data:
			recent_trend = daily_data[-3:] if len(daily_data) >= 3 else daily_data
			if len(recent_trend) > 1:
				trend = (
					"increasing"
					if recent_trend[-1]["daily_quantity"]
					> recent_trend[0]["daily_quantity"]
					else "decreasing"
				)
				if trend == "decreasing":
					recommendations.append(
						"Sales declining - review pricing and marketing strategy"
					)

		return recommendations

	async def _get_business_overview(
		self, start_date: datetime, end_date: datetime
	) -> dict[str, Any]:
		"""Get comprehensive business overview."""
		sales_query = select(
			func.sum(Sale.amount).label("total_revenue"),
			func.count(Sale.id).label("total_transactions"),
			func.avg(Sale.amount).label("avg_transaction_value"),
		).where(and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date))

		sales_result = await self.db.execute(sales_query)
		sales_data = sales_result.first()

		customer_query = select(func.count(Customer.id).label("total_customers"))
		customer_result = await self.db.execute(customer_query)
		customer_data = customer_result.first()

		product_query = select(
			func.count(Product.id).label("total_products"),
			func.count(Product.id).filter(Product.is_active).label("active_products"),
		)
		product_result = await self.db.execute(product_query)
		product_data = product_result.first()

		return {
			"period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
			"sales": {
				"total_revenue": float(sales_data.total_revenue or 0),
				"total_transactions": int(sales_data.total_transactions or 0),
				"avg_transaction_value": float(sales_data.avg_transaction_value or 0),
			},
			"customers": {"total_customers": int(customer_data.total_customers or 0)},
			"products": {
				"total_products": int(product_data.total_products or 0),
				"active_products": int(product_data.active_products or 0),
			},
		}

	async def _analyze_business_trends(
		self, start_date: datetime, end_date: datetime
	) -> dict[str, Any]:
		"""Analyze business trends."""
		daily_query = (
			select(
				func.date(Sale.sale_date).label("date"),
				func.sum(Sale.amount).label("daily_revenue"),
				func.count(Sale.id).label("daily_transactions"),
			)
			.where(and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date))
			.group_by(func.date(Sale.sale_date))
			.order_by(func.date(Sale.sale_date))
		)

		daily_result = await self.db.execute(daily_query)
		daily_data = [dict(row._mapping) for row in daily_result]

		return {
			"daily_trends": daily_data,
			"analysis": "Trend analysis based on daily performance data",
		}

	async def _detect_anomalies(
		self, start_date: datetime, end_date: datetime
	) -> dict[str, Any]:
		"""Detect anomalies in business data."""
		daily_query = (
			select(
				func.date(Sale.sale_date).label("date"),
				func.sum(Sale.amount).label("daily_revenue"),
			)
			.where(and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date))
			.group_by(func.date(Sale.sale_date))
			.order_by(func.date(Sale.sale_date))
		)

		daily_result = await self.db.execute(daily_query)
		daily_data = [dict(row._mapping) for row in daily_result]

		anomalies = []
		if len(daily_data) > 1:
			revenues = [day["daily_revenue"] for day in daily_data]
			mean_revenue = statistics.mean(revenues)
			std_revenue = statistics.stdev(revenues) if len(revenues) > 1 else 0

			for day in daily_data:
				if abs(day["daily_revenue"] - mean_revenue) > 2 * std_revenue:
					anomalies.append(
						{
							"date": day["date"],
							"revenue": day["daily_revenue"],
							"deviation": abs(day["daily_revenue"] - mean_revenue),
						}
					)

		return {"anomalies": anomalies, "total_anomalies": len(anomalies)}

	async def _generate_forecast(
		self, start_date: datetime, end_date: datetime
	) -> dict[str, Any]:
		"""Generate simple business forecast."""
		daily_query = (
			select(
				func.date(Sale.sale_date).label("date"),
				func.sum(Sale.amount).label("daily_revenue"),
			)
			.where(and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date))
			.group_by(func.date(Sale.sale_date))
			.order_by(func.date(Sale.sale_date))
		)

		daily_result = await self.db.execute(daily_query)
		daily_data = [dict(row._mapping) for row in daily_result]

		if len(daily_data) < 2:
			return {"forecast": "Insufficient data for forecasting"}

		revenues = [day["daily_revenue"] for day in daily_data]
		trend = (revenues[-1] - revenues[0]) / len(revenues) if len(revenues) > 1 else 0

		forecast = []
		last_revenue = revenues[-1]
		for i in range(1, 8):
			forecast_revenue = last_revenue + (trend * i)
			forecast.append(
				{
					"date": (end_date + timedelta(days=i)).strftime("%Y-%m-%d"),
					"predicted_revenue": max(0, forecast_revenue),
				}
			)

		return {
			"forecast": forecast,
			"trend": trend,
			"confidence": "medium",
		}

	async def _get_sales_metrics(
		self, start_date: datetime, end_date: datetime
	) -> dict[str, Any]:
		"""Get sales metrics for a period."""
		query = select(
			func.sum(Sale.amount).label("total_revenue"),
			func.count(Sale.id).label("total_transactions"),
			func.avg(Sale.amount).label("avg_transaction_value"),
		).where(and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date))

		result = await self.db.execute(query)
		data = result.first()

		return {
			"total_revenue": float(data.total_revenue or 0),
			"total_transactions": int(data.total_transactions or 0),
			"avg_transaction_value": float(data.avg_transaction_value or 0),
		}

	async def _get_customer_metrics(
		self, start_date: datetime, end_date: datetime
	) -> dict[str, Any]:
		"""Get customer metrics for a period."""
		new_customers_query = select(func.count(Customer.id)).where(
			and_(Customer.created_at >= start_date, Customer.created_at <= end_date)
		)
		new_customers_result = await self.db.execute(new_customers_query)
		new_customers = new_customers_result.scalar()

		active_customers_query = select(
			func.count(func.distinct(Sale.customer_id))
		).where(and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date))
		active_customers_result = await self.db.execute(active_customers_query)
		active_customers = active_customers_result.scalar()

		return {
			"new_customers": int(new_customers or 0),
			"active_customers": int(active_customers or 0),
		}

	async def _get_product_metrics(
		self, start_date: datetime, end_date: datetime
	) -> dict[str, Any]:
		"""Get product metrics for a period."""
		products_sold_query = select(func.count(func.distinct(Sale.product_id))).where(
			and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
		)
		products_sold_result = await self.db.execute(products_sold_query)
		products_sold = products_sold_result.scalar()

		total_products_query = select(func.count(Product.id)).where(Product.is_active)
		total_products_result = await self.db.execute(total_products_query)
		total_products = total_products_result.scalar()

		return {
			"products_sold": int(products_sold or 0),
			"total_products": int(total_products or 0),
		}

	def _calculate_change(
		self, period1: dict[str, Any], period2: dict[str, Any]
	) -> dict[str, Any]:
		"""Calculate percentage change between two periods."""
		changes = {}
		for key in period1.keys():
			if (
				key in period2
				and isinstance(period1[key], (int, float))
				and isinstance(period2[key], (int, float))
			):
				if period1[key] != 0:
					change_pct = ((period2[key] - period1[key]) / period1[key]) * 100
					changes[key] = {
						"absolute": period2[key] - period1[key],
						"percentage": round(change_pct, 2),
					}
				else:
					changes[key] = {
						"absolute": period2[key] - period1[key],
						"percentage": 100 if period2[key] > 0 else 0,
					}
		return changes

	async def _analyze_period_comparison(
		self, comparison: dict[str, Any]
	) -> dict[str, Any]:
		"""Analyze period comparison with AI insights."""
		analysis = {
			"summary": "Period comparison analysis",
			"key_insights": [],
			"recommendations": [],
		}

		for metric, data in comparison["metrics"].items():
			if "change" in data:
				for key, change in data["change"].items():
					if change["percentage"] > 10:
						analysis["key_insights"].append(
							f"{metric} {key} increased by {change['percentage']}%"
						)
					elif change["percentage"] < -10:
						analysis["key_insights"].append(
							f"{metric} {key} decreased by {abs(change['percentage'])}%"
						)

		return analysis

	async def _predict_customer_trends(
		self, customers_data: list[dict[str, Any]]
	) -> dict[str, Any]:
		"""Predict customer trends and behavior patterns."""
		predictions = {
			"trends": [],
			"insights": [],
			"recommendations": [],
		}

		if not customers_data:
			return predictions

		total_spent_values = [c["total_spent"] or 0 for c in customers_data]
		avg_spent = statistics.mean(total_spent_values) if total_spent_values else 0

		total_orders = [c["total_orders"] or 0 for c in customers_data]
		avg_orders = statistics.mean(total_orders) if total_orders else 0

		high_value_count = len(
			[c for c in customers_data if (c["total_spent"] or 0) > avg_spent * 1.5]
		)
		if high_value_count > len(customers_data) * 0.2:
			predictions["trends"].append("Growing high-value customer base")
			predictions["recommendations"].append(
				"Focus on retaining high-value customers"
			)

		if avg_orders > 3:
			predictions["trends"].append("Customers show high engagement")
			predictions["insights"].append("Strong customer loyalty patterns detected")
		elif avg_orders < 1.5:
			predictions["trends"].append("Low customer engagement")
			predictions["recommendations"].append(
				"Implement customer retention strategies"
			)

		recent_customers = [
			c
			for c in customers_data
			if c["last_purchase"] and (datetime.now() - c["last_purchase"]).days <= 30
		]
		recent_activity_ratio = (
			len(recent_customers) / len(customers_data) if customers_data else 0
		)

		if recent_activity_ratio > 0.7:
			predictions["trends"].append("High recent customer activity")
			predictions["insights"].append("Strong current customer engagement")
		elif recent_activity_ratio < 0.3:
			predictions["trends"].append("Declining customer activity")
			predictions["recommendations"].append("Launch re-engagement campaigns")

		return predictions
