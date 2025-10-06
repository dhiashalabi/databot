"""Invoice and InvoiceItem models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Invoice(Base):
	"""Invoice model."""

	__tablename__ = "invoice"

	id: Mapped[int] = mapped_column(primary_key=True)
	invoice_number: Mapped[str] = mapped_column(String(50), unique=True)
	customer_id: Mapped[int] = mapped_column(
		ForeignKey("customer.id", ondelete="RESTRICT")
	)
	invoice_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
	subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
	tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
	discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
	total_amount: Mapped[float] = mapped_column(Numeric(12, 2))
	status: Mapped[str] = mapped_column(String(50), default="pending")
	payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
	notes: Mapped[str | None] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
	)


class InvoiceItem(Base):
	"""Invoice line item model."""

	__tablename__ = "invoice_item"

	id: Mapped[int] = mapped_column(primary_key=True)
	invoice_id: Mapped[int] = mapped_column(
		ForeignKey("invoice.id", ondelete="CASCADE")
	)
	product_id: Mapped[int] = mapped_column(
		ForeignKey("product.id", ondelete="RESTRICT")
	)
	quantity: Mapped[int] = mapped_column(Integer)
	unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
	discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
	line_total: Mapped[float] = mapped_column(Numeric(12, 2))
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
