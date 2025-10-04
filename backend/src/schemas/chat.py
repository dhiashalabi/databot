"""Chat API schemas for AI-powered business assistant."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
	"""Request model for chat messages."""

	message: str
	model: str | None = None


class ChatResponse(BaseModel):
	"""Response model for chat messages."""

	answer: str
	data: list[dict] | dict | None = None
	query: str
	files: list[dict] | None = None
