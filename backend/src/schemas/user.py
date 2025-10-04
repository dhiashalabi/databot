"""User schemas for API requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
	"""Base user schema with common fields."""

	username: str
	email: EmailStr


class UserCreate(UserBase):
	"""Schema for creating a new user."""

	password: str

	@field_validator("password")
	@classmethod
	def validate_password_length(cls, v):
		"""Validate password length for bcrypt compatibility."""
		if len(v.encode("utf-8")) > 72:
			truncated = v.encode("utf-8")[:72].decode("utf-8", errors="ignore")
			return truncated
		return v


class UserUpdate(BaseModel):
	"""Schema for updating user information."""

	username: str | None = None
	email: EmailStr | None = None
	password: str | None = None
	is_active: bool | None = None
	is_admin: bool | None = None


class UserResponse(UserBase):
	"""Schema for user response data."""

	id: UUID
	is_active: bool
	is_admin: bool
	created_at: datetime
	updated_at: datetime

	class Config:
		"""Pydantic configuration."""

		from_attributes = True


class UserLogin(BaseModel):
	"""Schema for user login."""

	username: str
	password: str


class Token(BaseModel):
	"""Schema for authentication token."""

	access_token: str
	token_type: str


class TokenData(BaseModel):
	"""Schema for token data."""

	username: str | None = None
