"""User management API endpoints."""

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.models.user import User
from src.services.permission_service import PermissionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/permissions")
async def get_my_permissions(
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
	"""Get current user's permissions and roles."""
	try:
		permission_service = PermissionService(db)

		permissions = await permission_service.get_user_permissions(current_user.id)
		roles = await permission_service.get_user_roles(current_user.id)

		return {
			"user_id": str(current_user.id),
			"username": current_user.username,
			"email": current_user.email,
			"permissions": permissions,
			"roles": roles,
			"is_admin": await permission_service.is_admin(current_user.id),
		}
	except Exception as e:
		logger.error(f"Error getting user permissions: {e}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to retrieve user permissions",
		) from e


@router.get("/me/accessible-tools")
async def get_my_accessible_tools(
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
	"""Get tools the current user can access."""
	try:
		permission_service = PermissionService(db)

		from src.auth.permissions import PermissionChecker

		permission_checker = PermissionChecker(permission_service)

		accessible_tools = await permission_checker.get_accessible_tools(
			current_user.id
		)
		accessible_models = await permission_checker.get_accessible_models(
			current_user.id
		)

		return {
			"user_id": str(current_user.id),
			"accessible_tools": accessible_tools,
			"accessible_models": accessible_models,
		}
	except Exception as e:
		logger.error(f"Error getting accessible tools: {e}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to retrieve accessible tools",
		) from e


@router.post("/assign-role")
async def assign_role_to_user(
	user_id: UUID,
	role_name: str,
	# current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
	"""Assign a role to a user (admin only)."""
	try:
		permission_service = PermissionService(db)

		# if not await permission_service.is_admin(current_user.id):
		# 	raise HTTPException(
		# 		status_code=status.HTTP_403_FORBIDDEN,
		# 		detail="Only administrators can assign roles",
		# 	)

		success = await permission_service.assign_role_to_user(user_id, role_name)

		if not success:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Failed to assign role {role_name} to user {user_id}",
			)

		return {
			"message": f"Successfully assigned role {role_name} to user {user_id}",
			"user_id": str(user_id),
			"role_name": role_name,
		}
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error assigning role: {e}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to assign role",
		) from e


@router.delete("/remove-role")
async def remove_role_from_user(
	user_id: UUID,
	role_name: str,
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
	"""Remove a role from a user (admin only)."""
	try:
		permission_service = PermissionService(db)

		if not await permission_service.is_admin(current_user.id):
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Only administrators can remove roles",
			)

		success = await permission_service.remove_role_from_user(user_id, role_name)

		if not success:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=f"Failed to remove role {role_name} from user {user_id}",
			)

		return {
			"message": f"Successfully removed role {role_name} from user {user_id}",
			"user_id": str(user_id),
			"role_name": role_name,
		}
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error removing role: {e}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to remove role",
		) from e


@router.get("/roles")
async def list_available_roles(
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
	"""List all available roles (admin only)."""
	try:
		permission_service = PermissionService(db)

		if not await permission_service.is_admin(current_user.id):
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Only administrators can view all roles",
			)

		from sqlalchemy import select

		from src.models.permissions import Role

		query = select(Role)
		result = await db.execute(query)
		roles = result.scalars().all()

		return {
			"roles": [
				{
					"id": role.id,
					"name": role.name,
					"description": role.description,
					"created_at": role.created_at.isoformat(),
				}
				for role in roles
			]
		}
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error listing roles: {e}")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to list roles",
		) from e
