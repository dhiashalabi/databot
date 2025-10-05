"""API endpoints for AI feedback and chat history."""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.models.ai_feedback import AIFeedback, ChatHistory
from src.models.user import User
from src.schemas.token_feedback import (
	AIFeedbackCreate,
	AIFeedbackResponse,
	ChatHistoryResponse,
	FeedbackSummaryResponse,
	ModelPerformanceResponse,
)
from src.services.ai_feedback_service import AIFeedbackService
from src.services.permission_service import PermissionService

router = APIRouter()


@router.post("/feedback", response_model=AIFeedbackResponse)
async def submit_feedback(
	feedback: AIFeedbackCreate,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Submit feedback for an AI chat interaction."""
	try:
		feedback_service = AIFeedbackService(db)

		result = await db.execute(
			select(ChatHistory).where(ChatHistory.id == feedback.chat_history_id)
		)
		chat = result.scalar_one_or_none()

		if not chat:
			chat_history_id = uuid4()

			chat = ChatHistory(
				id=chat_history_id,
				user_id=current_user.id,
				user_query="Feedback submission without chat context",
				model_used="unknown",
				ai_response="N/A",
				total_tokens=0,
				success=True,
			)
			db.add(chat)
			await db.commit()
			await db.refresh(chat)
		else:
			if chat.user_id != current_user.id:
				raise HTTPException(
					status_code=403,
					detail="Cannot provide feedback for another user's chat",
				)
			chat_history_id = feedback.chat_history_id

		ai_feedback = await feedback_service.submit_feedback(
			user_id=current_user.id,
			chat_history_id=chat_history_id,
			feedback_type=feedback.feedback_type,
			rating=feedback.rating,
			is_liked=feedback.is_liked,
			feedback_text=feedback.feedback_text,
			helpfulness_rating=feedback.helpfulness_rating,
			accuracy_rating=feedback.accuracy_rating,
			relevance_rating=feedback.relevance_rating,
			suggested_improvements=feedback.suggested_improvements,
			reported_issues=feedback.reported_issues,
		)

		return AIFeedbackResponse.model_validate(ai_feedback)

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error submitting feedback: {str(e)}"
		) from e


@router.get("/feedback/{chat_history_id}", response_model=AIFeedbackResponse | None)
async def get_chat_feedback(
	chat_history_id: UUID,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Get feedback for a specific chat interaction."""
	try:
		feedback_service = AIFeedbackService(db)
		feedback = await feedback_service.get_chat_feedback(
			chat_history_id, current_user.id
		)

		if not feedback:
			return None

		return AIFeedbackResponse.model_validate(feedback)

	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting feedback: {str(e)}"
		) from e


@router.get("/chat-history", response_model=list[ChatHistoryResponse])
async def get_chat_history(
	limit: int = Query(10, description="Maximum number of records to return"),
	include_feedback: bool = Query(True, description="Include feedback information"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Get recent chat history for the current user."""
	try:
		feedback_service = AIFeedbackService(db)
		history = await feedback_service.get_recent_chat_history(
			user_id=current_user.id, limit=limit, include_feedback=include_feedback
		)

		return [ChatHistoryResponse(**chat) for chat in history]

	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting chat history: {str(e)}"
		) from e


@router.get("/feedback/summary", response_model=FeedbackSummaryResponse)
async def get_feedback_summary(
	days: int = Query(30, description="Number of days to include in summary"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Get feedback summary for the current user."""
	try:
		feedback_service = AIFeedbackService(db)
		summary = await feedback_service.get_user_feedback_summary(
			user_id=current_user.id, days=days
		)

		return FeedbackSummaryResponse(**summary)

	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting feedback summary: {str(e)}"
		) from e


@router.get("/admin/feedback/summary", response_model=FeedbackSummaryResponse)
async def get_system_feedback_summary(
	days: int = Query(30, description="Number of days to include in summary"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Get system-wide feedback summary (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "ai.tokens.view"
		):
			raise HTTPException(status_code=403, detail="Permission denied")

		feedback_service = AIFeedbackService(db)
		summary = await feedback_service.get_user_feedback_summary(
			user_id=None,
			days=days,
		)

		return FeedbackSummaryResponse(**summary)

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting system feedback summary: {str(e)}"
		) from e


@router.get("/admin/model-performance")
async def get_model_performance(
	model_name: str | None = Query(None, description="Specific model name (optional)"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
) -> dict[str, Any] | ModelPerformanceResponse:
	"""Get performance metrics for AI models based on feedback (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "ai.tokens.view"
		):
			raise HTTPException(status_code=403, detail="Permission denied")

		feedback_service = AIFeedbackService(db)
		metrics = await feedback_service.get_model_performance_metrics(model_name)

		if model_name:
			if not metrics:
				raise HTTPException(
					status_code=404, detail="Model not found or no data available"
				)
			return ModelPerformanceResponse(**metrics)
		else:
			return metrics

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting model performance: {str(e)}"
		) from e


@router.get("/admin/detailed-feedback")
async def get_detailed_feedback(
	days: int = Query(30, description="Number of days to include"),
	model_name: str | None = Query(None, description="Filter by model name"),
	feedback_type: str | None = Query(None, description="Filter by feedback type"),
	min_rating: int | None = Query(None, description="Minimum rating filter"),
	limit: int = Query(100, description="Maximum number of records"),
	offset: int = Query(0, description="Number of records to skip"),
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
	"""Get detailed feedback records with chat information (admin only)."""
	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(
			current_user.id, "ai.tokens.view"
		):
			raise HTTPException(status_code=403, detail="Permission denied")

		cutoff_date = datetime.utcnow() - timedelta(days=days)

		query = (
			select(
				AIFeedback,
				ChatHistory.user_query,
				ChatHistory.ai_response,
				ChatHistory.model_used,
				ChatHistory.total_tokens,
				ChatHistory.response_time_ms,
				ChatHistory.created_at.label("chat_created_at"),
			)
			.join(ChatHistory, AIFeedback.chat_history_id == ChatHistory.id)
			.where(AIFeedback.created_at >= cutoff_date)
		)

		if model_name:
			query = query.where(ChatHistory.model_used == model_name)
		if feedback_type:
			query = query.where(AIFeedback.feedback_type == feedback_type)
		if min_rating is not None:
			query = query.where(AIFeedback.rating >= min_rating)

		query = query.order_by(desc(AIFeedback.created_at)).offset(offset).limit(limit)

		result = await db.execute(query)
		records = result.all()

		detailed_feedback = []
		for record in records:
			feedback = record.AIFeedback
			detailed_feedback.append(
				{
					"feedback_id": str(feedback.id),
					"chat_history_id": str(feedback.chat_history_id),
					"user_id": str(feedback.user_id),
					"feedback_type": feedback.feedback_type.value,
					"rating": feedback.rating,
					"is_liked": feedback.is_liked,
					"feedback_text": feedback.feedback_text,
					"helpfulness_rating": feedback.helpfulness_rating,
					"accuracy_rating": feedback.accuracy_rating,
					"relevance_rating": feedback.relevance_rating,
					"suggested_improvements": feedback.suggested_improvements,
					"reported_issues": feedback.reported_issues,
					"feedback_created_at": feedback.created_at.isoformat(),
					"user_query": record.user_query,
					"ai_response": record.ai_response[:500] + "..."
					if record.ai_response and len(record.ai_response) > 500
					else record.ai_response,
					"model_used": record.model_used,
					"total_tokens": record.total_tokens,
					"response_time_ms": record.response_time_ms,
					"chat_created_at": record.chat_created_at.isoformat(),
				}
			)

		return detailed_feedback

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Error getting detailed feedback: {str(e)}"
		) from e


@router.delete("/feedback/{feedback_id}")
async def delete_feedback(
	feedback_id: UUID,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Delete feedback (user can only delete their own feedback)."""
	try:
		result = await db.execute(
			select(AIFeedback).where(AIFeedback.id == feedback_id)
		)
		feedback = result.scalar_one_or_none()

		if not feedback:
			raise HTTPException(status_code=404, detail="Feedback not found")

		if feedback.user_id != current_user.id:
			raise HTTPException(
				status_code=403, detail="Cannot delete another user's feedback"
			)

		await db.delete(feedback)
		await db.commit()

		return {"message": "Feedback deleted successfully"}

	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		raise HTTPException(
			status_code=500, detail=f"Error deleting feedback: {str(e)}"
		) from e
