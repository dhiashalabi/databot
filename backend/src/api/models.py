"""Models API endpoints for OpenAI model management."""

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.permissions import PermissionChecker
from src.config import settings
from src.database import get_db
from src.models.user import User
from src.schemas.models import ModelInfo, ModelsResponse
from src.services.permission_service import PermissionService

router = APIRouter()


@router.get("/models", response_model=ModelsResponse)
async def get_available_models(
	current_user: User = Depends(get_current_user),
	db: AsyncSession = Depends(get_db),
):
	"""Get available OpenAI models based on user permissions.

	Fetches the list of available models from OpenAI API and filters them
	based on the user's permissions. Only returns models the user can access.

	Returns:
		ModelsResponse: List of accessible models and default model

	Raises:
		HTTPException: If OpenAI API request fails or user lacks permissions
	"""
	if not settings.OPENAI_API_KEY:
		raise HTTPException(status_code=500, detail="OpenAI API key not configured")

	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(current_user.id, "ai.use"):
			raise HTTPException(
				status_code=403, detail="You don't have permission to access AI models"
			)

		permission_checker = PermissionChecker(permission_service)
		accessible_model_names = await permission_checker.get_accessible_models(
			current_user.id
		)

		if not accessible_model_names:
			return ModelsResponse(models=[], default_model=None)

		client = OpenAI(api_key=settings.OPENAI_API_KEY)
		response = client.models.list()

		available_models = [
			ModelInfo(
				id=model.id,
				object=model.object,
				created=model.created,
				owned_by=model.owned_by,
			)
			for model in response.data
			if model.id in accessible_model_names
		]

		default_model = (
			settings.OPENAI_MODEL
			if settings.OPENAI_MODEL in accessible_model_names
			else None
		)
		if not default_model and available_models:
			default_model = available_models[0].id

		return ModelsResponse(models=available_models, default_model=default_model)

	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Failed to fetch models: {str(e)}"
		) from e
