"""Customer model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Customer(Base):
	"""Customer model."""

	__tablename__ = "customer"

	id: Mapped[int] = mapped_column(primary_key=True)
	customer_name: Mapped[str] = mapped_column(String(255))
	email: Mapped[str] = mapped_column(String(255), unique=True)
	phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
	company: Mapped[str | None] = mapped_column(String(255), nullable=True)
	address: Mapped[str | None] = mapped_column(String(500), nullable=True)
	city: Mapped[str | None] = mapped_column(String(100), nullable=True)
	country: Mapped[str | None] = mapped_column(String(100), nullable=True)
	customer_type: Mapped[str] = mapped_column(String(50), default="retail")
	credit_limit: Mapped[float] = mapped_column(Float, default=0)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
	)
