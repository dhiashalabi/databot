"""Token usage tracking models for AI request management."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
	Boolean,
	CheckConstraint,
	Date,
	DateTime,
	ForeignKey,
	Index,
	Integer,
	Numeric,
	String,
	Text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
	from src.models.user import User


class FrequencyType(str, Enum):
	"""Frequency types for token limits."""

	DAILY = "daily"
	WEEKLY = "weekly"
	MONTHLY = "monthly"


class ModelTokenLimit(Base):
	"""Model-specific token limits and pricing."""

	__tablename__ = "model_token_limits"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	model_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

	daily_token_limit: Mapped[int] = mapped_column(Integer, nullable=True)
	weekly_token_limit: Mapped[int] = mapped_column(Integer, nullable=True)
	monthly_token_limit: Mapped[int] = mapped_column(Integer, nullable=True)

	input_cost_per_1k_tokens: Mapped[Decimal | None] = mapped_column(
		Numeric(10, 6), nullable=True
	)
	output_cost_per_1k_tokens: Mapped[Decimal | None] = mapped_column(
		Numeric(10, 6), nullable=True
	)

	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default="NOW()", nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default="NOW()",
		onupdate=datetime.utcnow,
		nullable=False,
	)

	def __repr__(self) -> str:
		return f"<ModelTokenLimit(model={self.model_name}, daily={self.daily_token_limit})>"


class TokenUsage(Base):
	"""Individual token usage records for tracking AI requests."""

	__tablename__ = "token_usage"

	id: Mapped[UUID] = mapped_column(
		PostgresUUID(as_uuid=True),
		primary_key=True,
		server_default="gen_random_uuid()",
	)
	user_id: Mapped[UUID] = mapped_column(
		PostgresUUID(as_uuid=True),
		ForeignKey("user.id", ondelete="CASCADE"),
		nullable=False,
	)
	model_name: Mapped[str] = mapped_column(String(100), nullable=False)

	input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

	input_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
	output_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
	total_cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)

	request_type: Mapped[str] = mapped_column(
		String(50), nullable=False, default="chat"
	)
	user_query: Mapped[str] = mapped_column(Text, nullable=True)
	response_summary: Mapped[str] = mapped_column(Text, nullable=True)

	response_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
	success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	error_message: Mapped[str] = mapped_column(Text, nullable=True)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default="NOW()", nullable=False
	)

	user: Mapped["User"] = relationship("User", back_populates="token_usage")

	__table_args__ = (
		CheckConstraint(
			"total_tokens = input_tokens + output_tokens", name="check_total_tokens"
		),
		Index("idx_token_usage_user_date", "user_id", "created_at"),
		Index("idx_token_usage_model_date", "model_name", "created_at"),
		Index("idx_token_usage_user_model", "user_id", "model_name"),
	)

	def __repr__(self) -> str:
		return f"<TokenUsage(user_id={self.user_id}, model={self.model_name}, tokens={self.total_tokens})>"


class UserTokenQuota(Base):
	"""User-specific token quotas and overrides."""

	__tablename__ = "user_token_quotas"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	user_id: Mapped[UUID] = mapped_column(
		PostgresUUID(as_uuid=True),
		ForeignKey("user.id", ondelete="CASCADE"),
		nullable=False,
	)
	model_name: Mapped[str] = mapped_column(String(100), nullable=False)

	daily_token_limit: Mapped[int] = mapped_column(Integer, nullable=True)
	weekly_token_limit: Mapped[int] = mapped_column(Integer, nullable=True)
	monthly_token_limit: Mapped[int] = mapped_column(Integer, nullable=True)

	daily_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	weekly_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
	monthly_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

	daily_reset_date: Mapped[date] = mapped_column(Date, nullable=True)
	weekly_reset_date: Mapped[date] = mapped_column(Date, nullable=True)
	monthly_reset_date: Mapped[date] = mapped_column(Date, nullable=True)

	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default="NOW()", nullable=False
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default="NOW()",
		onupdate=datetime.utcnow,
		nullable=False,
	)

	user: Mapped["User"] = relationship("User")

	__table_args__ = (
		Index("idx_user_token_quota_unique", "user_id", "model_name", unique=True),
		Index("idx_user_token_quota_user", "user_id"),
	)

	def __repr__(self) -> str:
		return f"<UserTokenQuota(user_id={self.user_id}, model={self.model_name})>"
