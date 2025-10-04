"""Invoice-specific query builders."""

from typing import Any

from sqlalchemy import desc, func, select

from src.models.invoice import Invoice

from .base import BaseQueryBuilder


class InvoiceQueryBuilder(BaseQueryBuilder):
	"""Specialized query builder for invoice operations."""

	@staticmethod
	def build_invoice_query(
		filters: dict[str, Any] | None = None, order_by: str | None = None
	):
		"""Build an invoice query with common filters."""
		query = select(Invoice)

		if not filters:
			return query

		if "invoice_number" in filters:
			query = query.where(Invoice.invoice_number == filters["invoice_number"])

		if "customer_id" in filters:
			query = query.where(Invoice.customer_id == filters["customer_id"])

		if "status" in filters:
			query = query.where(Invoice.status == filters["status"])

		if "payment_method" in filters:
			query = query.where(Invoice.payment_method == filters["payment_method"])

		if "total_amount" in filters and isinstance(filters["total_amount"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Invoice.total_amount, filters["total_amount"]
			)

		if "subtotal" in filters and isinstance(filters["subtotal"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Invoice.subtotal, filters["subtotal"]
			)

		if "invoice_date" in filters and isinstance(filters["invoice_date"], dict):
			query = BaseQueryBuilder.apply_date_filter(
				query, Invoice.invoice_date, filters["invoice_date"]
			)

		if "due_date" in filters and isinstance(filters["due_date"], dict):
			query = BaseQueryBuilder.apply_date_filter(
				query, Invoice.due_date, filters["due_date"]
			)

		query = BaseQueryBuilder.apply_ordering(
			query, Invoice, order_by, desc(Invoice.invoice_date)
		)

		return query

	@staticmethod
	def build_invoice_count_query(filters: dict[str, Any] | None = None):
		"""Build a count query for invoices with same filters."""
		query = select(func.count(Invoice.id))

		if not filters:
			return query

		if "invoice_number" in filters:
			query = query.where(Invoice.invoice_number == filters["invoice_number"])

		if "customer_id" in filters:
			query = query.where(Invoice.customer_id == filters["customer_id"])

		if "status" in filters:
			query = query.where(Invoice.status == filters["status"])

		if "payment_method" in filters:
			query = query.where(Invoice.payment_method == filters["payment_method"])

		if "total_amount" in filters and isinstance(filters["total_amount"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Invoice.total_amount, filters["total_amount"]
			)

		if "subtotal" in filters and isinstance(filters["subtotal"], dict):
			query = BaseQueryBuilder.apply_range_filter(
				query, Invoice.subtotal, filters["subtotal"]
			)

		if "invoice_date" in filters and isinstance(filters["invoice_date"], dict):
			query = BaseQueryBuilder.apply_date_filter(
				query, Invoice.invoice_date, filters["invoice_date"]
			)

		if "due_date" in filters and isinstance(filters["due_date"], dict):
			query = BaseQueryBuilder.apply_date_filter(
				query, Invoice.due_date, filters["due_date"]
			)

		return query

	@staticmethod
	def build_pending_invoices_query():
		"""Build query for pending invoices."""
		return (
			select(Invoice)
			.where(Invoice.status == "pending")
			.order_by(Invoice.due_date)
		)

	@staticmethod
	def build_invoice_summary_query(start_date: str | None = None):
		"""Build query for invoice summary."""
		from datetime import datetime

		query = select(
			func.count(Invoice.id).label("total_invoices"),
			func.sum(Invoice.total_amount).label("total_amount"),
			func.avg(Invoice.total_amount).label("avg_amount"),
			func.count(Invoice.id).filter(Invoice.status == "paid").label("paid_count"),
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

		return query
