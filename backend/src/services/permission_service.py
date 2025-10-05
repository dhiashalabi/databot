"""Permission service for role-based access control."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.permissions import (
	Permission,
	Role,
	RolePermission,
	ToolPermission,
	UserRole,
)

logger = logging.getLogger(__name__)


class PermissionService:
	"""Service for handling user permissions and role-based access control."""

	def __init__(self, db_session: AsyncSession):
		"""Initialize the permission service."""
		self.db = db_session

	async def user_has_permission(self, user_id: UUID, permission_code: str) -> bool:
		"""Check if a user has a specific permission.

		Args:
			user_id: The user's UUID
			permission_code: The permission code to check (e.g., "ai.use", "mcp.sales.view")

		Returns:
			True if user has the permission, False otherwise
		"""
		try:
			query = (
				select(Permission.id)
				.select_from(
					UserRole.__table__.join(
						RolePermission.__table__,
						UserRole.role_id == RolePermission.role_id,
					).join(
						Permission.__table__,
						RolePermission.permission_id == Permission.id,
					)
				)
				.where(
					and_(
						UserRole.user_id == user_id, Permission.code == permission_code
					)
				)
			)

			result = await self.db.execute(query)
			return result.scalar() is not None

		except Exception as e:
			logger.error(
				f"Error checking permission {permission_code} for user {user_id}: {e}"
			)
			return False

	async def user_has_any_permission(
		self, user_id: UUID, permission_codes: list[str]
	) -> bool:
		"""Check if a user has any of the specified permissions.

		Args:
			user_id: The user's UUID
			permission_codes: List of permission codes to check

		Returns:
			True if user has any of the permissions, False otherwise
		"""
		for permission_code in permission_codes:
			if await self.user_has_permission(user_id, permission_code):
				return True
		return False

	async def get_user_permissions(self, user_id: UUID) -> list[str]:
		"""Get all permissions for a user.

		Args:
			user_id: The user's UUID

		Returns:
			List of permission codes the user has
		"""
		try:
			from src.models.permissions import RolePermission

			query = (
				select(Permission.code)
				.select_from(
					UserRole.__table__.join(
						RolePermission.__table__,
						UserRole.role_id == RolePermission.role_id,
					).join(
						Permission.__table__,
						RolePermission.permission_id == Permission.id,
					)
				)
				.where(UserRole.user_id == user_id)
			)

			result = await self.db.execute(query)
			permissions = result.scalars().all()
			return list(permissions)

		except Exception as e:
			logger.error(f"Error getting permissions for user {user_id}: {e}")
			return []

	async def get_user_roles(self, user_id: UUID) -> list[dict[str, Any]]:
		"""Get all roles for a user.

		Args:
			user_id: The user's UUID

		Returns:
			List of role information
		"""
		try:
			query = (
				select(Role)
				.select_from(UserRole.__table__.join(Role.__table__))
				.where(UserRole.user_id == user_id)
			)

			result = await self.db.execute(query)
			roles = result.scalars().all()

			return [
				{"id": role.id, "name": role.name, "description": role.description}
				for role in roles
			]

		except Exception as e:
			logger.error(f"Error getting roles for user {user_id}: {e}")
			return []

	async def assign_role_to_user(self, user_id: UUID, role_name: str) -> bool:
		"""Assign a role to a user.

		Args:
			user_id: The user's UUID
			role_name: The name of the role to assign

		Returns:
			True if successful, False otherwise
		"""
		try:
			role_query = select(Role).where(Role.name == role_name)
			role_result = await self.db.execute(role_query)
			role = role_result.scalar_one_or_none()

			if not role:
				logger.error(f"Role {role_name} not found")
				return False

			existing_query = select(UserRole).where(
				and_(UserRole.user_id == user_id, UserRole.role_id == role.id)
			)
			existing_result = await self.db.execute(existing_query)
			if existing_result.scalar_one_or_none():
				logger.info(f"User {user_id} already has role {role_name}")
				return True

			user_role = UserRole(user_id=user_id, role_id=role.id)
			self.db.add(user_role)
			await self.db.commit()

			logger.info(f"Assigned role {role_name} to user {user_id}")
			return True

		except Exception as e:
			logger.error(f"Error assigning role {role_name} to user {user_id}: {e}")
			await self.db.rollback()
			return False

	async def remove_role_from_user(self, user_id: UUID, role_name: str) -> bool:
		"""Remove a role from a user.

		Args:
			user_id: The user's UUID
			role_name: The name of the role to remove

		Returns:
			True if successful, False otherwise
		"""
		try:
			role_query = select(Role).where(Role.name == role_name)
			role_result = await self.db.execute(role_query)
			role = role_result.scalar_one_or_none()

			if not role:
				logger.error(f"Role {role_name} not found")
				return False

			user_role_query = select(UserRole).where(
				and_(UserRole.user_id == user_id, UserRole.role_id == role.id)
			)
			user_role_result = await self.db.execute(user_role_query)
			user_role = user_role_result.scalar_one_or_none()

			if not user_role:
				logger.info(f"User {user_id} doesn't have role {role_name}")
				return True

			await self.db.delete(user_role)
			await self.db.commit()

			logger.info(f"Removed role {role_name} from user {user_id}")
			return True

		except Exception as e:
			logger.error(f"Error removing role {role_name} from user {user_id}: {e}")
			await self.db.rollback()
			return False

	async def tool_has_permission(self, tool_name: str, permission_code: str) -> bool:
		"""Check if a tool requires a specific permission.

		Args:
			tool_name: The name of the MCP tool
			permission_code: The permission code to check

		Returns:
			True if the tool requires this permission, False otherwise
		"""
		try:
			query = select(ToolPermission).where(
				and_(
					ToolPermission.tool_name == tool_name,
					ToolPermission.permission_code == permission_code,
					ToolPermission.is_enabled,
				)
			)

			result = await self.db.execute(query)
			return result.scalar_one_or_none() is not None

		except Exception as e:
			logger.error(f"Error checking tool permission for {tool_name}: {e}")
			return False

	async def get_required_permission_for_tool(self, tool_name: str) -> str | None:
		"""Get the required permission for a specific tool.

		Args:
			tool_name: The name of the MCP tool

		Returns:
			The permission code required for the tool, or None if not found
		"""
		try:
			query = select(ToolPermission.permission_code).where(
				and_(ToolPermission.tool_name == tool_name, ToolPermission.is_enabled)
			)

			result = await self.db.execute(query)
			return result.scalar_one_or_none()

		except Exception as e:
			logger.error(f"Error getting required permission for tool {tool_name}: {e}")
			return None

	async def check_ai_model_permission(self, user_id: UUID, model_name: str) -> bool:
		"""Check if a user can use a specific AI model.

		Args:
			user_id: The user's UUID
			model_name: The AI model name (e.g., "gpt-4o", "gpt-3.5-turbo")

		Returns:
			True if user can use the model, False otherwise
		"""
		if await self.user_has_permission(user_id, "ai.use"):
			model_permission = f"ai.model.{model_name}.use"
			return await self.user_has_permission(user_id, model_permission)

		return False

	async def is_admin(self, user_id: UUID) -> bool:
		"""Check if a user is an admin.

		Args:
			user_id: The user's UUID

		Returns:
			True if user is admin, False otherwise
		"""
		user_roles = await self.get_user_roles(user_id)
		return any(role["name"] == "admin" for role in user_roles)
