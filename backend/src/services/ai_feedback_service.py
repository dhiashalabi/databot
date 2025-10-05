"""AI feedback management service."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ai_feedback import AIFeedback, ChatHistory, FeedbackType


class AIFeedbackService:
	"""Service for managing AI feedback and chat history."""

	def __init__(self, db: AsyncSession):
		"""Initialize the AI feedback service."""
		self.db = db
		self.logger = logging.getLogger(__name__)

	async def submit_feedback(
		self,
		user_id: UUID,
		chat_history_id: UUID,
		feedback_type: FeedbackType,
		rating: int | None = None,
		is_liked: bool | None = None,
		feedback_text: str | None = None,
		helpfulness_rating: int | None = None,
		accuracy_rating: int | None = None,
		relevance_rating: int | None = None,
		suggested_improvements: str | None = None,
		reported_issues: str | None = None,
	) -> AIFeedback:
		"""Submit feedback for a chat interaction."""
		try:
			existing_feedback = await self.db.execute(
				select(AIFeedback).where(
					and_(
						AIFeedback.user_id == user_id,
						AIFeedback.chat_history_id == chat_history_id,
					)
				)
			)
			existing = existing_feedback.scalar_one_or_none()

			if existing:
				existing.feedback_type = feedback_type
				existing.rating = rating
				existing.is_liked = is_liked
				existing.feedback_text = feedback_text
				existing.helpfulness_rating = helpfulness_rating
				existing.accuracy_rating = accuracy_rating
				existing.relevance_rating = relevance_rating
				existing.suggested_improvements = suggested_improvements
				existing.reported_issues = reported_issues

				await self.db.commit()
				await self.db.refresh(existing)

				self.logger.info(f"Updated feedback for chat {chat_history_id}")
				return existing
			else:
				feedback = AIFeedback(
					user_id=user_id,
					chat_history_id=chat_history_id,
					feedback_type=feedback_type,
					rating=rating,
					is_liked=is_liked,
					feedback_text=feedback_text,
					helpfulness_rating=helpfulness_rating,
					accuracy_rating=accuracy_rating,
					relevance_rating=relevance_rating,
					suggested_improvements=suggested_improvements,
					reported_issues=reported_issues,
				)

				self.db.add(feedback)
				await self.db.commit()
				await self.db.refresh(feedback)

				self.logger.info(f"Created feedback for chat {chat_history_id}")
				return feedback

		except Exception as e:
			self.logger.error(f"Error submitting feedback: {e}")
			await self.db.rollback()
			raise

	async def get_chat_feedback(
		self, chat_history_id: UUID, user_id: UUID | None = None
	) -> AIFeedback | None:
		"""Get feedback for a specific chat interaction."""
		try:
			query = select(AIFeedback).where(
				AIFeedback.chat_history_id == chat_history_id
			)

			if user_id:
				query = query.where(AIFeedback.user_id == user_id)

			result = await self.db.execute(query)
			return result.scalar_one_or_none()

		except Exception as e:
			self.logger.error(f"Error getting chat feedback: {e}")
			return None

	async def get_user_feedback_summary(
		self, user_id: UUID | None = None, days: int = 30
	) -> dict[str, Any]:
		"""Get feedback summary for a user or all users."""
		try:
			query = select(
				func.count(AIFeedback.id).label("total_feedback"),
				func.count(case((AIFeedback.is_liked.is_(True), 1))).label(
					"liked_count"
				),
				func.count(case((AIFeedback.is_liked.is_(False), 1))).label(
					"disliked_count"
				),
				func.avg(AIFeedback.rating).label("avg_rating"),
				func.avg(AIFeedback.helpfulness_rating).label("avg_helpfulness"),
				func.avg(AIFeedback.accuracy_rating).label("avg_accuracy"),
				func.avg(AIFeedback.relevance_rating).label("avg_relevance"),
			)

			if user_id:
				query = query.where(AIFeedback.user_id == user_id)

			if days > 0:
				from datetime import datetime, timedelta

				query = query.where(
					AIFeedback.created_at >= datetime.utcnow() - timedelta(days=days)
				)

			result = await self.db.execute(query)
			row = result.first()

			if not row or row.total_feedback == 0:
				return {
					"total_feedback": 0,
					"liked_count": 0,
					"disliked_count": 0,
					"like_percentage": 0.0,
					"avg_rating": 0.0,
					"avg_helpfulness": 0.0,
					"avg_accuracy": 0.0,
					"avg_relevance": 0.0,
				}

			like_percentage = (
				(row.liked_count / row.total_feedback) * 100
				if row.total_feedback > 0
				else 0.0
			)

			return {
				"total_feedback": row.total_feedback,
				"liked_count": row.liked_count or 0,
				"disliked_count": row.disliked_count or 0,
				"like_percentage": round(like_percentage, 2),
				"avg_rating": round(float(row.avg_rating or 0), 2),
				"avg_helpfulness": round(float(row.avg_helpfulness or 0), 2),
				"avg_accuracy": round(float(row.avg_accuracy or 0), 2),
				"avg_relevance": round(float(row.avg_relevance or 0), 2),
			}

		except Exception as e:
			self.logger.error(f"Error getting feedback summary: {e}")
			return {}

	async def get_recent_chat_history(
		self, user_id: UUID, limit: int = 10, include_feedback: bool = True
	) -> list[dict[str, Any]]:
		"""Get recent chat history for a user with optional feedback."""
		try:
			query = (
				select(ChatHistory)
				.where(ChatHistory.user_id == user_id)
				.order_by(ChatHistory.created_at.desc())
				.limit(limit)
			)

			result = await self.db.execute(query)
			chat_records = result.scalars().all()

			if not include_feedback:
				return [
					{
						"id": str(chat.id),
						"user_query": chat.user_query,
						"ai_response": chat.ai_response,
						"model_used": chat.model_used,
						"total_tokens": chat.total_tokens,
						"response_time_ms": chat.response_time_ms,
						"success": chat.success,
						"created_at": chat.created_at.isoformat(),
					}
					for chat in chat_records
				]

			chat_ids = [chat.id for chat in chat_records]
			feedback_query = select(AIFeedback).where(
				AIFeedback.chat_history_id.in_(chat_ids)
			)
			feedback_result = await self.db.execute(feedback_query)
			feedback_records = {
				fb.chat_history_id: fb for fb in feedback_result.scalars().all()
			}

			return [
				{
					"id": str(chat.id),
					"user_query": chat.user_query,
					"ai_response": chat.ai_response,
					"model_used": chat.model_used,
					"total_tokens": chat.total_tokens,
					"response_time_ms": chat.response_time_ms,
					"success": chat.success,
					"created_at": chat.created_at.isoformat(),
					"feedback": {
						"has_feedback": chat.id in feedback_records,
						"feedback_type": feedback_records[chat.id].feedback_type.value
						if chat.id in feedback_records
						else None,
						"is_liked": feedback_records[chat.id].is_liked
						if chat.id in feedback_records
						else None,
						"rating": feedback_records[chat.id].rating
						if chat.id in feedback_records
						else None,
						"feedback_text": feedback_records[chat.id].feedback_text
						if chat.id in feedback_records
						else None,
					},
				}
				for chat in chat_records
			]

		except Exception as e:
			self.logger.error(f"Error getting chat history: {e}")
			return []

	async def get_model_performance_metrics(
		self, model_name: str | None = None
	) -> dict[str, Any]:
		"""Get performance metrics for AI models based on feedback."""
		try:
			query = (
				select(
					ChatHistory.model_used,
					func.count(ChatHistory.id).label("total_chats"),
					func.count(AIFeedback.id).label("feedback_count"),
					func.avg(ChatHistory.response_time_ms).label("avg_response_time"),
					func.avg(ChatHistory.total_tokens).label("avg_tokens"),
					func.count(case((AIFeedback.is_liked.is_(True), 1))).label(
						"liked_count"
					),
					func.avg(AIFeedback.rating).label("avg_rating"),
					func.avg(AIFeedback.helpfulness_rating).label("avg_helpfulness"),
				)
				.select_from(ChatHistory.__table__.outerjoin(AIFeedback.__table__))
				.group_by(ChatHistory.model_used)
			)

			if model_name:
				query = query.where(ChatHistory.model_used == model_name)

			result = await self.db.execute(query)
			rows = result.all()

			metrics = []
			for row in rows:
				feedback_rate = (
					(row.feedback_count / row.total_chats) * 100
					if row.total_chats > 0
					else 0.0
				)
				satisfaction_rate = (
					(row.liked_count / row.feedback_count) * 100
					if row.feedback_count > 0
					else 0.0
				)

				metrics.append(
					{
						"model_name": row.model_used,
						"total_chats": row.total_chats,
						"feedback_count": row.feedback_count,
						"feedback_rate": round(feedback_rate, 2),
						"satisfaction_rate": round(satisfaction_rate, 2),
						"avg_response_time": round(
							float(row.avg_response_time or 0), 2
						),
						"avg_tokens": round(float(row.avg_tokens or 0), 2),
						"avg_rating": round(float(row.avg_rating or 0), 2),
						"avg_helpfulness": round(float(row.avg_helpfulness or 0), 2),
					}
				)

			return (
				{"models": metrics} if not model_name else metrics[0] if metrics else {}
			)

		except Exception as e:
			self.logger.error(f"Error getting model performance metrics: {e}")
			return {}
