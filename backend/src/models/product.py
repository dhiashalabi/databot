"""Product and Category models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Category(Base):
	"""Product category model."""

	__tablename__ = "category"

	id: Mapped[int] = mapped_column(primary_key=True)
	category_name: Mapped[str] = mapped_column(String(100), unique=True)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	parent_category_id: Mapped[int | None] = mapped_column(
		ForeignKey("category.id", ondelete="SET NULL"), nullable=True
	)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
	"""Product model."""

	__tablename__ = "product"

	id: Mapped[int] = mapped_column(primary_key=True)
	product_name: Mapped[str] = mapped_column(String(255))
	sku: Mapped[str] = mapped_column(String(100), unique=True)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	category_id: Mapped[int | None] = mapped_column(
		ForeignKey("category.id", ondelete="SET NULL"), nullable=True
	)
	unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
	cost_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
	stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
	reorder_level: Mapped[int] = mapped_column(Integer, default=10)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
	)
