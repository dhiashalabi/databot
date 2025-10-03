"""Sales model for tracking sales data."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Sale(Base):
	"""Sales record model."""

	__tablename__ = "sale"

	id: Mapped[int] = mapped_column(primary_key=True)
	customer_id: Mapped[int | None] = mapped_column(
		ForeignKey("customer.id", ondelete="SET NULL"), nullable=True
	)
	product_id: Mapped[int | None] = mapped_column(
		ForeignKey("product.id", ondelete="SET NULL"), nullable=True
	)
	invoice_id: Mapped[int | None] = mapped_column(
		ForeignKey("invoice.id", ondelete="SET NULL"), nullable=True
	)
	product_name: Mapped[str] = mapped_column(String(255))
	amount: Mapped[float] = mapped_column(Float)
	quantity: Mapped[int] = mapped_column(default=1)
	sale_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
	category: Mapped[str | None] = mapped_column(String(100), nullable=True)
	payment_status: Mapped[str] = mapped_column(String(50), default="completed")
	sales_channel: Mapped[str] = mapped_column(String(50), default="online")
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
