"""AI Permission middleware for protecting model access."""

import logging
from typing import Any
from uuid import UUID

from src.auth.permissions import PermissionChecker
from src.services.permission_service import PermissionService

logger = logging.getLogger(__name__)


class AIPermissionMiddleware:
	"""Middleware to enforce permissions on AI model calls."""

	def __init__(self, permission_service: PermissionService):
		"""Initialize the middleware with permission service."""
		self.permission_service = permission_service
		self.permission_checker = PermissionChecker(permission_service)

	async def check_model_permission(
		self, user_id: UUID, model_name: str, messages: list[dict[str, Any]]
	) -> bool:
		"""Check if user has permission to use a specific AI model.

		Args:
			user_id: The user's UUID
			model_name: Name of the AI model being used
			messages: Messages being sent to the model

		Returns:
			True if user has permission, False otherwise
		"""
		if not user_id:
			logger.error("User ID is required for permission check")
			return False

		if not model_name:
			logger.error("Model name is required for permission check")
			return False

		try:
			await self.permission_checker.validate_ai_model_call(
				user_id=user_id, model_name=model_name, messages=messages
			)
			return True
		except PermissionError as e:
			logger.warning(
				f"Permission denied for user {user_id} on model {model_name}: {e}"
			)
			return False
		except Exception as e:
			logger.error(f"Error checking model permission: {e}")
			return False

	async def get_available_models(self, user_id: UUID) -> list[str]:
		"""Get list of AI models the user can access.

		Args:
			user_id: The user's UUID

		Returns:
			List of model names the user can access
		"""
		try:
			return await self.permission_checker.get_accessible_models(user_id)
		except Exception as e:
			logger.error(f"Error getting available models for user {user_id}: {e}")
			return []

	async def validate_token_permissions(self, user_id: UUID) -> bool:
		"""Check if user has permission to view token usage.

		Args:
			user_id: The user's UUID

		Returns:
			True if user can view token usage, False otherwise
		"""
		try:
			return await self.permission_service.user_has_permission(
				user_id, "ai.tokens.view"
			)
		except Exception as e:
			logger.error(f"Error checking token permissions for user {user_id}: {e}")
			return False

	async def can_manage_tokens(self, user_id: UUID) -> bool:
		"""Check if user has permission to manage token settings.

		Args:
			user_id: The user's UUID

		Returns:
			True if user can manage tokens, False otherwise
		"""
		try:
			return await self.permission_service.user_has_permission(
				user_id, "ai.tokens.manage"
			)
		except Exception as e:
			logger.error(
				f"Error checking token management permissions for user {user_id}: {e}"
			)
			return False

	def create_permission_error_response(
		self, model_name: str, user_id: UUID
	) -> dict[str, Any]:
		"""Create a standardized permission error response.

		Args:
			model_name: Name of the model that was denied
			user_id: The user's UUID

		Returns:
			Error response dictionary
		"""
		return {
			"error": "PermissionDenied",
			"message": f"You don't have permission to use the '{model_name}' model",
			"model_name": model_name,
			"user_id": str(user_id),
			"type": "permission_error",
		}
