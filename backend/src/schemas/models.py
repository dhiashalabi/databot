"""Models API schemas for OpenAI model management."""

from pydantic import BaseModel


class ModelInfo(BaseModel):
	"""Information about an OpenAI model."""

	id: str
	object: str
	created: int
	owned_by: str


class ModelsResponse(BaseModel):
	"""Response model for available OpenAI models."""

	models: list[ModelInfo]
	default_model: str
