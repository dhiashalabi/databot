"""API endpoints for token management and usage tracking."""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.errors.exceptions import TokenLimitExceeded
from src.models.token_usage import ModelTokenLimit, TokenUsage, UserTokenQuota
from src.models.user import User
from src.schemas.token_feedback import (
	ModelTokenLimitCreate,
	ModelTokenLimitResponse,
	TokenLimitsResponse,
	TokenUsageResponse,
	UsageSummaryResponse,
	UserTokenQuotaCreate,
	UserTokenQuotaResponse,
)
from src.services.permission_service import PermissionService
from src.services.token_management_service import TokenManagementService

router = APIRouter()


@router.get("/limits/check", response_model=TokenLimitsResponse)
async def check_token_limits(
	model_name: str = Query(..., description="Model name to check limits for"),
	requested_tokens: int = Query(
		0, description="Number of tokens for the planned request"
	),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Check if user can make a request based on current token limits."""
	try:
		token_service = TokenManagementService(db)
		limits_check = await token_service.check_token_limits(
			current_user.id, model_name, requested_tokens
		)

		return TokenLimitsResponse(**limits_check)

	except TokenLimitExceeded as e:
		raise HTTPException(
			status_code=429,
			detail={
				"error": "Token limit exceeded",
				"message": e.message,
				"error_code": e.error_code,
				"limit_type": e.limit_type,
				"allowed": False,
				"reason": e.message,
			},
		) from e
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error checking token limits: {str(e)}"
		) from e


@router.get("/usage/summary", response_model=UsageSummaryResponse)
async def get_usage_summary(
	model_name: str | None = Query(None, description="Specific model name (optional)"),
	days: int = Query(30, description="Number of days to include in summary"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Get token usage summary for the current user."""
	try:
		token_service = TokenManagementService(db)
		summary = await token_service.get_user_usage_summary(
			current_user.id, model_name, days
		)

		return UsageSummaryResponse(**summary)

	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting usage summary: {str(e)}"
		) from e


@router.get("/usage/history")
async def get_usage_history(
	model_name: str | None = Query(None, description="Filter by model name"),
	limit: int = Query(50, description="Maximum number of records to return"),
	offset: int = Query(0, description="Number of records to skip"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
) -> list[TokenUsageResponse]:
	"""Get detailed token usage history for the current user."""
	try:
		query = select(TokenUsage).where(TokenUsage.user_id == current_user.id)

		if model_name:
			query = query.where(TokenUsage.model_name == model_name)

		query = query.order_by(desc(TokenUsage.created_at)).offset(offset).limit(limit)

		result = await db.execute(query)
		usage_records = result.scalars().all()

		return [TokenUsageResponse.model_validate(record) for record in usage_records]

	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting usage history: {str(e)}"
		) from e


@router.post("/admin/model-limits", response_model=ModelTokenLimitResponse)
async def create_model_limits(
	limits: ModelTokenLimitCreate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Create or update token limits for a model (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "ai.tokens.manage"
		):
			raise HTTPException(
				status_code=403, detail="Permission denied: Admin access required"
			)

		result = await db.execute(
			select(ModelTokenLimit).where(
				ModelTokenLimit.model_name == limits.model_name
			)
		)
		existing = result.scalar_one_or_none()

		if existing:
			existing.daily_token_limit = limits.daily_token_limit
			existing.weekly_token_limit = limits.weekly_token_limit
			existing.monthly_token_limit = limits.monthly_token_limit
			existing.input_cost_per_1k_tokens = limits.input_cost_per_1k_tokens
			existing.output_cost_per_1k_tokens = limits.output_cost_per_1k_tokens

			await db.commit()
			await db.refresh(existing)
			return ModelTokenLimitResponse.model_validate(existing)
		else:
			new_limits = ModelTokenLimit(**limits.model_dump())
			db.add(new_limits)
			await db.commit()
			await db.refresh(new_limits)
			return ModelTokenLimitResponse.model_validate(new_limits)

	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, detail=f"Error creating model limits: {str(e)}"
		) from e


@router.get("/admin/model-limits")
async def get_model_limits(
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
) -> list[ModelTokenLimitResponse]:
	"""Get all model token limits (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "ai.tokens.view"
		):
			raise HTTPException(status_code=403, detail="Permission denied")

		result = await db.execute(
			select(ModelTokenLimit).where(ModelTokenLimit.is_active)
		)
		limits = result.scalars().all()

		return [ModelTokenLimitResponse.model_validate(limit) for limit in limits]

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting model limits: {str(e)}"
		) from e


@router.post("/admin/user-quotas", response_model=UserTokenQuotaResponse)
async def create_user_quota(
	quota: UserTokenQuotaCreate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Create or update user-specific token quota (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "ai.tokens.manage"
		):
			raise HTTPException(
				status_code=403, detail="Permission denied: Admin access required"
			)

		result = await db.execute(
			select(UserTokenQuota).where(
				and_(
					UserTokenQuota.user_id == quota.user_id,
					UserTokenQuota.model_name == quota.model_name,
				)
			)
		)
		existing = result.scalar_one_or_none()

		if existing:
			existing.daily_token_limit = quota.daily_token_limit
			existing.weekly_token_limit = quota.weekly_token_limit
			existing.monthly_token_limit = quota.monthly_token_limit

			await db.commit()
			await db.refresh(existing)
			return UserTokenQuotaResponse.model_validate(existing)
		else:
			# Create new
			new_quota = UserTokenQuota(**quota.model_dump())
			db.add(new_quota)
			await db.commit()
			await db.refresh(new_quota)
			return UserTokenQuotaResponse.model_validate(new_quota)

	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, detail=f"Error creating user quota: {str(e)}"
		) from e


@router.patch("/admin/users/{user_id}/ai-enabled")
async def toggle_user_ai_enabled(
	user_id: UUID,
	enabled: bool,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Enable or disable AI for a specific user (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "system.users.manage"
		):
			raise HTTPException(
				status_code=403, detail="Permission denied: Admin access required"
			)

		result = await db.execute(select(User).where(User.id == user_id))
		user = result.scalar_one_or_none()

		if not user:
			raise HTTPException(status_code=404, detail="User not found")

		await db.execute(
			update(User).where(User.id == user_id).values(ai_enabled=enabled)
		)
		await db.commit()

		return {
			"user_id": str(user_id),
			"ai_enabled": enabled,
			"message": f"AI {'enabled' if enabled else 'disabled'} for user",
		}

	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, detail=f"Error updating user AI status: {str(e)}"
		) from e


@router.get("/admin/usage/analytics")
async def get_usage_analytics(
	days: int = Query(30, description="Number of days to analyze"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
	"""Get system-wide token usage analytics (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "ai.tokens.view"
		):
			raise HTTPException(status_code=403, detail="Permission denied")

		cutoff_date = datetime.utcnow() - timedelta(days=days)

		model_usage_query = (
			select(
				TokenUsage.model_name,
				func.count(TokenUsage.id).label("request_count"),
				func.sum(TokenUsage.total_tokens).label("total_tokens"),
				func.sum(TokenUsage.total_cost).label("total_cost"),
				func.avg(TokenUsage.response_time_ms).label("avg_response_time"),
			)
			.where(TokenUsage.created_at >= cutoff_date)
			.group_by(TokenUsage.model_name)
		)

		result = await db.execute(model_usage_query)
		model_stats = result.all()

		overall_query = select(
			func.count(TokenUsage.id).label("total_requests"),
			func.sum(TokenUsage.total_tokens).label("total_tokens"),
			func.sum(TokenUsage.total_cost).label("total_cost"),
			func.count(func.distinct(TokenUsage.user_id)).label("active_users"),
		).where(TokenUsage.created_at >= cutoff_date)

		overall_result = await db.execute(overall_query)
		overall_stats = overall_result.first()

		return {
			"period_days": days,
			"overall": {
				"total_requests": overall_stats.total_requests or 0,
				"total_tokens": overall_stats.total_tokens or 0,
				"total_cost": float(overall_stats.total_cost or 0),
				"active_users": overall_stats.active_users or 0,
			},
			"by_model": [
				{
					"model_name": stat.model_name,
					"request_count": stat.request_count,
					"total_tokens": stat.total_tokens,
					"total_cost": float(stat.total_cost or 0),
					"avg_response_time": float(stat.avg_response_time or 0),
				}
				for stat in model_stats
			],
		}

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting usage analytics: {str(e)}"
		) from e
