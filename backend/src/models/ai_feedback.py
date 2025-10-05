"""AI feedback and chat history models."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
	Boolean,
	DateTime,
	ForeignKey,
	Index,
	Integer,
	String,
	Text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
	from src.models.user import User


class FeedbackType(str, Enum):
	"""Types of feedback that can be provided."""

	THUMBS_UP = "thumbs_up"
	THUMBS_DOWN = "thumbs_down"
	RATING = "rating"
	DETAILED = "detailed"


class ChatHistory(Base):
	"""Chat history and AI interaction logs."""

	__tablename__ = "chat_history"

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

	user_query: Mapped[str] = mapped_column(Text, nullable=False)
	model_used: Mapped[str] = mapped_column(String(100), nullable=False)

	ai_response: Mapped[str] = mapped_column(Text, nullable=True)
	response_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)

	input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

	request_type: Mapped[str] = mapped_column(
		String(50), nullable=False, default="chat"
	)
	tools_used: Mapped[str] = mapped_column(Text, nullable=True)
	success: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	error_message: Mapped[str] = mapped_column(Text, nullable=True)

	session_id: Mapped[str] = mapped_column(String(100), nullable=True)
	conversation_context: Mapped[str] = mapped_column(Text, nullable=True)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default="NOW()", nullable=False
	)

	user: Mapped["User"] = relationship("User", back_populates="chat_history")
	feedback: Mapped[list["AIFeedback"]] = relationship(
		"AIFeedback", back_populates="chat_history", cascade="all, delete-orphan"
	)

	__table_args__ = (
		Index("idx_chat_history_user_date", "user_id", "created_at"),
		Index("idx_chat_history_model", "model_used"),
		Index("idx_chat_history_session", "session_id"),
		Index("idx_chat_history_success", "success"),
	)

	def __repr__(self) -> str:
		return f"<ChatHistory(user_id={self.user_id}, model={self.model_used}, tokens={self.total_tokens})>"


class AIFeedback(Base):
	"""User feedback on AI responses."""

	__tablename__ = "ai_feedback"

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
	chat_history_id: Mapped[UUID] = mapped_column(
		PostgresUUID(as_uuid=True),
		ForeignKey("chat_history.id", ondelete="CASCADE"),
		nullable=False,
	)

	feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)
	rating: Mapped[int] = mapped_column(Integer, nullable=True)
	is_liked: Mapped[bool] = mapped_column(Boolean, nullable=True)
	feedback_text: Mapped[str] = mapped_column(Text, nullable=True)

	helpfulness_rating: Mapped[int] = mapped_column(Integer, nullable=True)
	accuracy_rating: Mapped[int] = mapped_column(Integer, nullable=True)
	relevance_rating: Mapped[int] = mapped_column(Integer, nullable=True)

	suggested_improvements: Mapped[str] = mapped_column(Text, nullable=True)
	reported_issues: Mapped[str] = mapped_column(Text, nullable=True)

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
	chat_history: Mapped[ChatHistory] = relationship(
		"ChatHistory", back_populates="feedback"
	)

	__table_args__ = (
		Index("idx_ai_feedback_user", "user_id"),
		Index("idx_ai_feedback_chat", "chat_history_id"),
		Index("idx_ai_feedback_type", "feedback_type"),
		Index("idx_ai_feedback_rating", "rating"),
		Index("idx_ai_feedback_liked", "is_liked"),
		Index("idx_ai_feedback_unique", "user_id", "chat_history_id", unique=True),
	)

	def __repr__(self) -> str:
		return f"<AIFeedback(user_id={self.user_id}, type={self.feedback_type}, liked={self.is_liked})>"
