"""Models API endpoints for OpenAI model management."""

from fastapi import APIRouter, HTTPException
from openai import OpenAI

from src.config import settings
from src.schemas.models import ModelInfo, ModelsResponse

router = APIRouter()


@router.get("/models", response_model=ModelsResponse)
async def get_available_models():
	"""Get all available OpenAI models.

	Fetches the list of available models from OpenAI API and returns
	them along with the default model from environment configuration.

	Returns:
		ModelsResponse: List of available models and default model

	Raises:
		HTTPException: If OpenAI API request fails
	"""
	if not settings.OPENAI_API_KEY:
		raise HTTPException(status_code=500, detail="OpenAI API key not configured")

	try:
		client = OpenAI(api_key=settings.OPENAI_API_KEY)
		response = client.models.list()

		models = [
			ModelInfo(
				id=model.id,
				object=model.object,
				created=model.created,
				owned_by=model.owned_by,
			)
			for model in response.data
		]

		return ModelsResponse(models=models, default_model=settings.OPENAI_MODEL)

	except Exception as e:
		raise HTTPException(
			status_code=500, detail=f"Failed to fetch models: {str(e)}"
		) from e
