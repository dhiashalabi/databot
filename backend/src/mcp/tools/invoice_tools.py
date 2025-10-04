"""Invoice-related tools for MCP server."""

from datetime import datetime
from typing import Any

from sqlalchemy import func, select

from src.models.invoice import Invoice
from src.queries import InvoiceQueryBuilder

from .base_tools import BaseTools


class InvoiceTools(BaseTools):
	"""Tools for invoice data analysis and querying."""

	async def get_pending_invoices(self) -> list:
		"""Get all pending invoices."""
		try:
			query = InvoiceQueryBuilder.build_pending_invoices_query()
			result = await self.db.execute(query)
			invoices = result.scalars().all()

			return [self._format_invoice_data(invoice) for invoice in invoices]
		except Exception:
			return []

	async def get_invoice_summary(
		self, start_date: str | None = None
	) -> dict[str, Any]:
		"""Get invoice summary with optional date filter."""
		try:
			query = select(
				func.count(Invoice.id).label("total_invoices"),
				func.sum(Invoice.total_amount).label("total_amount"),
				func.avg(Invoice.total_amount).label("avg_amount"),
				func.count(Invoice.id)
				.filter(Invoice.status == "paid")
				.label("paid_count"),
				func.count(Invoice.id)
				.filter(Invoice.status == "pending")
				.label("pending_count"),
				func.sum(Invoice.total_amount)
				.filter(Invoice.status == "paid")
				.label("paid_amount"),
				func.sum(Invoice.total_amount)
				.filter(Invoice.status == "pending")
				.label("pending_amount"),
			)

			if start_date:
				start = datetime.fromisoformat(start_date)
				query = query.where(Invoice.invoice_date >= start)

			result = await self.db.execute(query)
			summary = result.fetchone()

			return {
				"total_invoices": summary.total_invoices,
				"total_amount": float(summary.total_amount or 0),
				"avg_amount": float(summary.avg_amount or 0),
				"paid_count": summary.paid_count,
				"pending_count": summary.pending_count,
				"paid_amount": float(summary.paid_amount or 0),
				"pending_amount": float(summary.pending_amount or 0),
			}
		except Exception as e:
			return {"error": f"Error getting invoice summary: {str(e)}"}

	async def get_revenue_by_channel(self, start_date: str | None = None) -> list:
		"""Get revenue breakdown by sales channel."""
		try:
			from src.models.sales import Sale

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
				start = datetime.fromisoformat(start_date)
				query = query.where(Sale.sale_date >= start)

			result = await self.db.execute(query)
			channels = result.fetchall()

			return [
				{
					"sales_channel": channel.sales_channel,
					"total_revenue": float(channel.total_revenue),
					"transaction_count": channel.transaction_count,
					"avg_transaction": float(channel.avg_transaction),
				}
				for channel in channels
			]
		except Exception:
			return []

	async def get_invoices(
		self,
		filters: dict[str, Any] | None = None,
		order_by: str | None = None,
		limit: int | None = None,
		offset: int = 0,
	) -> dict[str, Any]:
		"""Get invoices with flexible filtering by any property."""
		try:
			query = InvoiceQueryBuilder.build_invoice_query(filters, order_by)
			query = InvoiceQueryBuilder.apply_pagination(query, limit, offset)

			result = await self.db.execute(query)
			invoices = result.scalars().all()

			count_query = InvoiceQueryBuilder.build_invoice_count_query(filters)
			count_result = await self.db.execute(count_query)
			total_count = count_result.scalar()

			invoices_data = [self._format_invoice_data(invoice) for invoice in invoices]

			return {
				"invoices": invoices_data,
				"summary": {
					"total_count": total_count,
					"returned_count": len(invoices_data),
					"total_amount": sum(
						float(invoice.total_amount) for invoice in invoices
					),
					"paid_count": sum(1 for i in invoices if i.status == "paid"),
					"pending_count": sum(1 for i in invoices if i.status == "pending"),
				},
			}
		except Exception as e:
			return {
				"error": f"Error querying invoices: {str(e)}",
				"error_type": type(e).__name__,
				"invoices": [],
				"summary": {
					"total_count": 0,
					"returned_count": 0,
					"total_amount": 0,
					"paid_count": 0,
					"pending_count": 0,
				},
			}
