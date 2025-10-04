"""Authentication dependencies for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_utils import verify_token
from src.database import get_db
from src.models.user import User

security = HTTPBearer()


async def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(security),
	db: AsyncSession = Depends(get_db),
) -> User:
	"""Get the current authenticated user."""
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	token = credentials.credentials
	username = verify_token(token)
	if username is None:
		raise credentials_exception

	result = await db.execute(select(User).where(User.username == username))
	user = result.scalar_one_or_none()
	if user is None:
		raise credentials_exception

	return user


async def get_current_active_user(
	current_user: User = Depends(get_current_user),
) -> User:
	"""Get the current active user."""
	if not current_user.is_active:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
		)
	return current_user


async def get_current_admin_user(
	current_user: User = Depends(get_current_active_user),
) -> User:
	"""Get the current admin user."""
	if not current_user.is_admin:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
		)
	return current_user
