"""Authentication API endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.models.user import User
from src.schemas.user import Token, UserLogin, UserResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
	user_credentials: UserLogin,
	db: AsyncSession = Depends(get_db),
):
	"""Login and get access token."""
	user_service = UserService(db)

	user = await user_service.authenticate_user(
		user_credentials.username, user_credentials.password
	)

	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)

	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
		data={"sub": user.username}, expires_delta=access_token_expires
	)

	return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
	current_user: User = Depends(get_current_active_user),
):
	"""Get current user information."""
	return UserResponse.model_validate(current_user)
