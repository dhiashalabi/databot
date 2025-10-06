"""Token management service for AI request tracking and limits."""

from datetime import datetime, timedelta
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai_feedback import ChatHistory
from src.models.token_usage import ModelTokenLimit, TokenUsage, UserTokenQuota
from src.models.user import User


class TokenManagementService:
	"""Service for managing AI token usage, limits, and tracking."""

	def __init__(self, db: AsyncSession):
		"""Initialize the token management service."""
		self.db = db
		self.logger = logging.getLogger(__name__)

	async def check_user_ai_enabled(self, user_id: UUID) -> bool:
		"""Check if AI is enabled for the user."""
		try:
			result = await self.db.execute(
				select(User.ai_enabled).where(User.id == user_id)
			)
			user_ai_enabled = result.scalar_one_or_none()
			return user_ai_enabled is True
		except Exception as e:
			self.logger.error(
				f"Error checking AI enabled status for user {user_id}: {e}"
			)
			return False

	async def get_model_limits(self, model_name: str) -> ModelTokenLimit | None:
		"""Get token limits for a specific model."""
		try:
			result = await self.db.execute(
				select(ModelTokenLimit).where(
					and_(
						ModelTokenLimit.model_name == model_name,
						ModelTokenLimit.is_active,
					)
				)
			)
			return result.scalar_one_or_none()
		except Exception as e:
			self.logger.error(f"Error getting model limits for {model_name}: {e}")
			return None

	async def get_user_quota(
		self, user_id: UUID, model_name: str
	) -> UserTokenQuota | None:
		"""Get user-specific quota for a model."""
		try:
			result = await self.db.execute(
				select(UserTokenQuota).where(
					and_(
						UserTokenQuota.user_id == user_id,
						UserTokenQuota.model_name == model_name,
						UserTokenQuota.is_active,
					)
				)
			)
			return result.scalar_one_or_none()
		except Exception as e:
			self.logger.error(
				f"Error getting user quota for {user_id}, {model_name}: {e}"
			)
			return None

	async def get_user_usage_in_period(
		self, user_id: UUID, model_name: str, period_type: str, start_date: datetime
	) -> int:
		"""Get user's token usage in a specific period."""
		try:
			result = await self.db.execute(
				select(func.coalesce(func.sum(TokenUsage.total_tokens), 0)).where(
					and_(
						TokenUsage.user_id == user_id,
						TokenUsage.model_name == model_name,
						TokenUsage.created_at >= start_date,
						TokenUsage.success,
					)
				)
			)
			return result.scalar() or 0
		except Exception as e:
			self.logger.error(f"Error getting usage for {user_id}, {model_name}: {e}")
			return 0

	async def check_token_limits(
		self, user_id: UUID, model_name: str, requested_tokens: int = 0
	) -> dict[str, Any]:
		"""Check if user can make a request based on token limits."""
		try:
			if not await self.check_user_ai_enabled(user_id):
				return {
					"allowed": False,
					"reason": "AI is disabled for this user",
					"limits": {},
				}

			model_limits = await self.get_model_limits(model_name)
			if not model_limits:
				self.logger.warning(
					f"No limits found for model {model_name}, allowing request"
				)
				return {
					"allowed": True,
					"reason": "No limits configured for model",
					"limits": {},
				}

			user_quota = await self.get_user_quota(user_id, model_name)

			now = datetime.utcnow()
			today = now.date()
			week_start = today - timedelta(days=today.weekday())
			month_start = today.replace(day=1)

			daily_start = datetime.combine(today, datetime.min.time())
			weekly_start = datetime.combine(week_start, datetime.min.time())
			monthly_start = datetime.combine(month_start, datetime.min.time())

			daily_usage = await self.get_user_usage_in_period(
				user_id, model_name, "daily", daily_start
			)
			weekly_usage = await self.get_user_usage_in_period(
				user_id, model_name, "weekly", weekly_start
			)
			monthly_usage = await self.get_user_usage_in_period(
				user_id, model_name, "monthly", monthly_start
			)

			daily_limit = (
				user_quota.daily_token_limit
				if user_quota and user_quota.daily_token_limit
				else model_limits.daily_token_limit
			)
			weekly_limit = (
				user_quota.weekly_token_limit
				if user_quota and user_quota.weekly_token_limit
				else model_limits.weekly_token_limit
			)
			monthly_limit = (
				user_quota.monthly_token_limit
				if user_quota and user_quota.monthly_token_limit
				else model_limits.monthly_token_limit
			)

			limits_info = {
				"daily": {
					"limit": daily_limit,
					"used": daily_usage,
					"remaining": (daily_limit - daily_usage) if daily_limit else None,
					"exceeded": daily_limit
					and (daily_usage + requested_tokens) > daily_limit,
				},
				"weekly": {
					"limit": weekly_limit,
					"used": weekly_usage,
					"remaining": (weekly_limit - weekly_usage)
					if weekly_limit
					else None,
					"exceeded": weekly_limit
					and (weekly_usage + requested_tokens) > weekly_limit,
				},
				"monthly": {
					"limit": monthly_limit,
					"used": monthly_usage,
					"remaining": (monthly_limit - monthly_usage)
					if monthly_limit
					else None,
					"exceeded": monthly_limit
					and (monthly_usage + requested_tokens) > monthly_limit,
				},
			}

			exceeded_periods = [
				period for period, info in limits_info.items() if info["exceeded"]
			]

			if exceeded_periods:
				return {
					"allowed": False,
					"reason": f"Token limit exceeded for: {', '.join(exceeded_periods)}",
					"limits": limits_info,
					"exceeded_periods": exceeded_periods,
				}

			return {
				"allowed": True,
				"reason": "Within token limits",
				"limits": limits_info,
			}

		except Exception as e:
			self.logger.error(f"Error checking token limits: {e}")
			return {
				"allowed": False,
				"reason": "Error checking token limits",
				"limits": {},
			}

	async def record_token_usage(
		self,
		user_id: UUID,
		model_name: str,
		input_tokens: int,
		output_tokens: int,
		request_type: str = "chat",
		user_query: str | None = None,
		response_summary: str | None = None,
		response_time_ms: int | None = None,
		success: bool = True,
		error_message: str | None = None,
	) -> TokenUsage:
		"""Record token usage for a user request."""
		try:
			model_limits = await self.get_model_limits(model_name)

			input_cost = None
			output_cost = None
			total_cost = None

			if model_limits:
				if model_limits.input_cost_per_1k_tokens:
					input_cost = (
						input_tokens / 1000
					) * model_limits.input_cost_per_1k_tokens
				if model_limits.output_cost_per_1k_tokens:
					output_cost = (
						output_tokens / 1000
					) * model_limits.output_cost_per_1k_tokens
				if input_cost is not None and output_cost is not None:
					total_cost = input_cost + output_cost

			total_tokens_calculated = max(0, input_tokens) + max(0, output_tokens)

			usage_record = TokenUsage(
				user_id=user_id,
				model_name=model_name,
				input_tokens=max(0, input_tokens),
				output_tokens=max(0, output_tokens),
				total_tokens=total_tokens_calculated,
				input_cost=input_cost,
				output_cost=output_cost,
				total_cost=total_cost,
				request_type=request_type,
				user_query=user_query[:2000] if user_query else None,
				response_summary=response_summary[:500] if response_summary else None,
				response_time_ms=response_time_ms,
				success=success,
				error_message=error_message[:1000] if error_message else None,
			)

			self.db.add(usage_record)
			await self.db.commit()
			await self.db.refresh(usage_record)

			self.logger.info(
				f"Recorded token usage: {total_tokens_calculated} tokens for user {user_id}"
			)
			return usage_record

		except Exception as e:
			self.logger.error(f"Error recording token usage: {e}")
			await self.db.rollback()
			raise

	async def create_chat_history(
		self,
		user_id: UUID,
		user_query: str,
		model_used: str,
		ai_response: str | None = None,
		response_time_ms: int | None = None,
		input_tokens: int = 0,
		output_tokens: int = 0,
		request_type: str = "chat",
		tools_used: str | None = None,
		success: bool = True,
		error_message: str | None = None,
		session_id: str | None = None,
		conversation_context: str | None = None,
	) -> ChatHistory:
		"""Create a chat history record."""
		try:
			chat_record = ChatHistory(
				user_id=user_id,
				user_query=user_query,
				model_used=model_used,
				ai_response=ai_response,
				response_time_ms=response_time_ms,
				input_tokens=input_tokens,
				output_tokens=output_tokens,
				total_tokens=input_tokens + output_tokens,
				request_type=request_type,
				tools_used=tools_used,
				success=success,
				error_message=error_message,
				session_id=session_id,
				conversation_context=conversation_context,
			)

			self.db.add(chat_record)
			await self.db.commit()
			await self.db.refresh(chat_record)

			self.logger.info(f"Created chat history record for user {user_id}")
			return chat_record

		except Exception as e:
			self.logger.error(f"Error creating chat history: {e}")
			await self.db.rollback()
			raise

	async def get_user_usage_summary(
		self, user_id: UUID, model_name: str | None = None, days: int = 30
	) -> dict[str, Any]:
		"""Get usage summary for a user."""
		try:
			query = select(
				func.count(TokenUsage.id).label("total_requests"),
				func.sum(TokenUsage.total_tokens).label("total_tokens"),
				func.sum(TokenUsage.input_tokens).label("total_input_tokens"),
				func.sum(TokenUsage.output_tokens).label("total_output_tokens"),
				func.sum(TokenUsage.total_cost).label("total_cost"),
				func.avg(TokenUsage.response_time_ms).label("avg_response_time"),
				func.count(case((TokenUsage.success, 1))).label("successful_requests"),
			).where(
				and_(
					TokenUsage.user_id == user_id,
					TokenUsage.created_at >= datetime.utcnow() - timedelta(days=days),
				)
			)

			if model_name:
				query = query.where(TokenUsage.model_name == model_name)

			result = await self.db.execute(query)
			row = result.first()

			if not row:
				return {
					"total_requests": 0,
					"total_tokens": 0,
					"total_input_tokens": 0,
					"total_output_tokens": 0,
					"total_cost": 0.0,
					"avg_response_time": 0,
					"successful_requests": 0,
					"success_rate": 0.0,
				}

			success_rate = (
				(row.successful_requests / row.total_requests) * 100
				if row.total_requests > 0
				else 0.0
			)

			return {
				"total_requests": row.total_requests or 0,
				"total_tokens": row.total_tokens or 0,
				"total_input_tokens": row.total_input_tokens or 0,
				"total_output_tokens": row.total_output_tokens or 0,
				"total_cost": float(row.total_cost or 0.0),
				"avg_response_time": float(row.avg_response_time or 0),
				"successful_requests": row.successful_requests or 0,
				"success_rate": round(success_rate, 2),
			}

		except Exception as e:
			self.logger.error(f"Error getting usage summary: {e}")
			return {}
