"""MCP Permission middleware for protecting tool access."""

import logging
from typing import Any
from uuid import UUID

from src.auth.permissions import PermissionChecker
from src.services.permission_service import PermissionService

logger = logging.getLogger(__name__)


class MCPPermissionMiddleware:
	"""Middleware to enforce permissions on MCP tool calls."""

	def __init__(self, permission_service: PermissionService):
		"""Initialize the middleware with permission service."""
		self.permission_service = permission_service
		self.permission_checker = PermissionChecker(permission_service)

	async def check_tool_permission(
		self, user_id: UUID, tool_name: str, arguments: dict[str, Any]
	) -> bool:
		"""Check if user has permission to use a specific tool.

		Args:
			user_id: The user's UUID
			tool_name: Name of the MCP tool being called
			arguments: Arguments being passed to the tool

		Returns:
			True if user has permission, False otherwise
		"""
		try:
			await self.permission_checker.validate_mcp_tool_call(
				user_id=user_id, tool_name=tool_name, arguments=arguments
			)
			return True
		except PermissionError as e:
			logger.warning(
				f"Permission denied for user {user_id} on tool {tool_name}: {e}"
			)
			return False
		except Exception as e:
			logger.error(f"Error checking tool permission: {e}")
			return False

	async def filter_available_tools(
		self, user_id: UUID, all_tools: list[str]
	) -> list[str]:
		"""Filter tools based on user permissions.

		Args:
			user_id: The user's UUID
			all_tools: List of all available tool names

		Returns:
			List of tools the user can access
		"""
		try:
			accessible_tools = await self.permission_checker.get_accessible_tools(
				user_id
			)
			return [tool for tool in all_tools if tool in accessible_tools]
		except Exception as e:
			logger.error(f"Error filtering tools for user {user_id}: {e}")
			return []

	def create_permission_error_response(
		self, tool_name: str, user_id: UUID
	) -> dict[str, Any]:
		"""Create a standardized permission error response.

		Args:
			tool_name: Name of the tool that was denied
			user_id: The user's UUID

		Returns:
			Error response dictionary
		"""
		return {
			"error": "PermissionDenied",
			"message": f"You don't have permission to use the '{tool_name}' tool",
			"tool_name": tool_name,
			"user_id": str(user_id),
			"type": "permission_error",
		}
