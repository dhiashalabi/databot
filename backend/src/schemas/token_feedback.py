"""Schemas for token management and AI feedback."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackTypeEnum(str, Enum):
	"""Types of feedback that can be provided."""

	THUMBS_UP = "thumbs_up"
	THUMBS_DOWN = "thumbs_down"
	RATING = "rating"
	DETAILED = "detailed"


class TokenUsageResponse(BaseModel):
	"""Response schema for token usage information."""

	id: UUID
	model_name: str
	input_tokens: int
	output_tokens: int
	total_tokens: int
	input_cost: Decimal | None = None
	output_cost: Decimal | None = None
	total_cost: Decimal | None = None
	request_type: str
	response_time_ms: int | None = None
	success: bool
	created_at: datetime

	class Config:
		from_attributes = True


class TokenLimitsResponse(BaseModel):
	"""Response schema for token limits check."""

	allowed: bool
	reason: str
	limits: dict[str, Any]


class TokenLimitErrorResponse(BaseModel):
	"""Response schema for token limit exceeded errors."""

	error: str = "Token limit exceeded"
	message: str
	error_code: str = "TOKEN_LIMIT_EXCEEDED"
	limit_type: str | None = None
	allowed: bool = False
	reason: str
	current_usage: int | None = None
	limit: int | None = None
	details: dict[str, Any] = Field(default_factory=dict)


class UsageSummaryResponse(BaseModel):
	"""Response schema for usage summary."""

	total_requests: int
	total_tokens: int
	total_input_tokens: int
	total_output_tokens: int
	total_cost: Decimal
	avg_response_time: float
	successful_requests: int
	success_rate: float


class AIFeedbackCreate(BaseModel):
	"""Schema for creating AI feedback."""

	chat_history_id: UUID
	feedback_type: FeedbackTypeEnum
	rating: int | None = Field(None, ge=1, le=5)
	is_liked: bool | None = None
	feedback_text: str | None = None
	helpfulness_rating: int | None = Field(None, ge=1, le=5)
	accuracy_rating: int | None = Field(None, ge=1, le=5)
	relevance_rating: int | None = Field(None, ge=1, le=5)
	suggested_improvements: str | None = None
	reported_issues: str | None = None


class AIFeedbackResponse(BaseModel):
	"""Response schema for AI feedback."""

	id: UUID
	chat_history_id: UUID
	feedback_type: FeedbackTypeEnum
	rating: int | None = None
	is_liked: bool | None = None
	feedback_text: str | None = None
	helpfulness_rating: int | None = None
	accuracy_rating: int | None = None
	relevance_rating: int | None = None
	suggested_improvements: str | None = None
	reported_issues: str | None = None
	created_at: datetime

	class Config:
		from_attributes = True


class ChatHistoryResponse(BaseModel):
	"""Response schema for chat history."""

	id: str
	user_query: str
	ai_response: str | None = None
	model_used: str
	total_tokens: int
	response_time_ms: int | None = None
	success: bool
	created_at: str
	feedback: dict[str, Any] | None = None


class FeedbackSummaryResponse(BaseModel):
	"""Response schema for feedback summary."""

	total_feedback: int
	liked_count: int
	disliked_count: int
	like_percentage: float
	avg_rating: float
	avg_helpfulness: float
	avg_accuracy: float
	avg_relevance: float


class ModelPerformanceResponse(BaseModel):
	"""Response schema for model performance metrics."""

	model_name: str
	total_chats: int
	feedback_count: int
	feedback_rate: float
	satisfaction_rate: float
	avg_response_time: float
	avg_tokens: float
	avg_rating: float
	avg_helpfulness: float


class ModelTokenLimitCreate(BaseModel):
	"""Schema for creating model token limits."""

	model_name: str
	daily_token_limit: int | None = None
	weekly_token_limit: int | None = None
	monthly_token_limit: int | None = None
	input_cost_per_1k_tokens: Decimal | None = None
	output_cost_per_1k_tokens: Decimal | None = None


class ModelTokenLimitResponse(BaseModel):
	"""Response schema for model token limits."""

	id: int
	model_name: str
	daily_token_limit: int | None = None
	weekly_token_limit: int | None = None
	monthly_token_limit: int | None = None
	input_cost_per_1k_tokens: Decimal | None = None
	output_cost_per_1k_tokens: Decimal | None = None
	is_active: bool
	created_at: datetime

	class Config:
		from_attributes = True


class UserTokenQuotaCreate(BaseModel):
	"""Schema for creating user token quotas."""

	user_id: UUID
	model_name: str
	daily_token_limit: int | None = None
	weekly_token_limit: int | None = None
	monthly_token_limit: int | None = None


class UserTokenQuotaResponse(BaseModel):
	"""Response schema for user token quotas."""

	id: int
	user_id: UUID
	model_name: str
	daily_token_limit: int | None = None
	weekly_token_limit: int | None = None
	monthly_token_limit: int | None = None
	daily_usage: int
	weekly_usage: int
	monthly_usage: int
	is_active: bool
	created_at: datetime

	class Config:
		from_attributes = True
