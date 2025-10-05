"""Permission decorators and middleware for MCP tools and AI access."""

from collections.abc import Callable
from functools import wraps
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select

from src.models.permissions import ToolPermission
from src.services.permission_service import PermissionService

logger = logging.getLogger(__name__)


def require_permission(permission_code: str):
	"""Decorator to require a specific permission for a function.

	Args:
		permission_code: The permission code required (e.g., "mcp.sales.view")
	"""

	def decorator(func: Callable) -> Callable:
		@wraps(func)
		async def wrapper(*args, **kwargs):
			user_id = kwargs.get("user_id")
			permission_service = kwargs.get("permission_service")

			if not user_id:
				raise ValueError("User ID is required for permission check")

			if not permission_service:
				raise ValueError("Permission service is required for permission check")

			if not await permission_service.user_has_permission(
				user_id, permission_code
			):
				raise PermissionError(f"Permission denied: {permission_code} required")

			return await func(*args, **kwargs)

		return wrapper

	return decorator


def require_any_permission(permission_codes: list[str]):
	"""Decorator to require any of the specified permissions for a function.

	Args:
		permission_codes: List of permission codes, user needs at least one
	"""

	def decorator(func: Callable) -> Callable:
		@wraps(func)
		async def wrapper(*args, **kwargs):
			user_id = kwargs.get("user_id")
			permission_service = kwargs.get("permission_service")

			if not user_id:
				raise ValueError("User ID is required for permission check")

			if not permission_service:
				raise ValueError("Permission service is required for permission check")

			if not await permission_service.user_has_any_permission(
				user_id, permission_codes
			):
				raise PermissionError(
					f"Permission denied: One of {permission_codes} required"
				)

			return await func(*args, **kwargs)

		return wrapper

	return decorator


class PermissionChecker:
	"""Utility class for permission checking in MCP tools and AI services."""

	def __init__(self, permission_service: PermissionService):
		"""Initialize the permission checker."""
		self.permission_service = permission_service

	async def check_mcp_tool_access(self, user_id: UUID, tool_name: str) -> bool:
		"""Check if a user can access a specific MCP tool.

		Args:
			user_id: The user's UUID
			tool_name: The name of the MCP tool

		Returns:
			True if user can access the tool, False otherwise
		"""
		try:
			required_permission = (
				await self.permission_service.get_required_permission_for_tool(
					tool_name
				)
			)

			if not required_permission:
				logger.warning(f"No permission mapping found for tool {tool_name}")
				required_permission = "mcp.tools.use"

			return await self.permission_service.user_has_permission(
				user_id, required_permission
			)

		except Exception as e:
			logger.error(f"Error checking MCP tool access for {tool_name}: {e}")
			return False

	async def check_ai_model_access(self, user_id: UUID, model_name: str) -> bool:
		"""Check if a user can access a specific AI model.

		Args:
			user_id: The user's UUID
			model_name: The AI model name (e.g., "gpt-4o", "gpt-3.5-turbo")

		Returns:
			True if user can access the model, False otherwise
		"""
		return await self.permission_service.check_ai_model_permission(
			user_id, model_name
		)

	async def validate_mcp_tool_call(
		self, user_id: UUID, tool_name: str, arguments: dict[str, Any]
	) -> None:
		"""Validate that a user can make a specific MCP tool call.

		Args:
			user_id: The user's UUID
			tool_name: The name of the MCP tool
			arguments: The arguments being passed to the tool

		Raises:
			PermissionError: If user doesn't have permission to use the tool
		"""
		if not await self.check_mcp_tool_access(user_id, tool_name):
			raise PermissionError(
				f"Permission denied: Cannot access MCP tool '{tool_name}'"
			)

		logger.info(f"User {user_id} authorized to use MCP tool '{tool_name}'")

	async def validate_ai_model_call(
		self, user_id: UUID, model_name: str, messages: list[dict]
	) -> None:
		"""Validate that a user can make a specific AI model call.

		Args:
			user_id: The user's UUID
			model_name: The AI model name
			messages: The messages being sent to the model

		Raises:
			PermissionError: If user doesn't have permission to use the model
		"""
		if not await self.check_ai_model_access(user_id, model_name):
			raise PermissionError(
				f"Permission denied: Cannot access AI model '{model_name}'"
			)

		logger.info(f"User {user_id} authorized to use AI model '{model_name}'")

	async def get_accessible_tools(self, user_id: UUID) -> list[str]:
		"""Get a list of all MCP tools the user can access.

		Args:
			user_id: The user's UUID

		Returns:
			List of tool names the user can access
		"""
		try:
			user_permissions = await self.permission_service.get_user_permissions(
				user_id
			)

			query = select(
				ToolPermission.tool_name, ToolPermission.permission_code
			).where(ToolPermission.is_enabled)

			result = await self.permission_service.db.execute(query)
			tool_mappings = result.fetchall()

			accessible_tools = []
			for tool_name, permission_code in tool_mappings:
				if permission_code in user_permissions:
					accessible_tools.append(tool_name)

			return accessible_tools

		except Exception as e:
			logger.error(f"Error getting accessible tools for user {user_id}: {e}")
			return []

	async def get_accessible_models(self, user_id: UUID) -> list[str]:
		"""Get a list of all AI models the user can access.

		Args:
			user_id: The user's UUID

		Returns:
			List of model names the user can access
		"""
		try:
			user_permissions = await self.permission_service.get_user_permissions(
				user_id
			)

			if "ai.use" not in user_permissions:
				return []

			available_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
			accessible_models = []

			for model in available_models:
				model_permission = f"ai.model.{model}.use"
				if model_permission in user_permissions:
					accessible_models.append(model)

			return accessible_models

		except Exception as e:
			logger.error(f"Error getting accessible models for user {user_id}: {e}")
			return []
