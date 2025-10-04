"""User service for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.auth_utils import get_password_hash, verify_password
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


class UserService:
	"""Service class for user operations."""

	def __init__(self, db: AsyncSession):
		"""Initialize the user service."""
		self.db = db

	async def get_user_by_id(self, user_id: UUID) -> User | None:
		"""Get a user by ID."""
		result = await self.db.execute(select(User).where(User.id == user_id))
		return result.scalar_one_or_none()

	async def get_user_by_username(self, username: str) -> User | None:
		"""Get a user by username."""
		result = await self.db.execute(select(User).where(User.username == username))
		return result.scalar_one_or_none()

	async def get_user_by_email(self, email: str) -> User | None:
		"""Get a user by email."""
		result = await self.db.execute(select(User).where(User.email == email))
		return result.scalar_one_or_none()

	async def create_user(self, user_data: UserCreate) -> User:
		"""Create a new user."""
		existing_user = await self.get_user_by_username(user_data.username)
		if existing_user:
			raise ValueError("Username already exists")

		existing_email = await self.get_user_by_email(user_data.email)
		if existing_email:
			raise ValueError("Email already exists")

		hashed_password = get_password_hash(user_data.password)
		user = User(
			username=user_data.username,
			email=user_data.email,
			hashed_password=hashed_password,
		)

		self.db.add(user)
		await self.db.commit()
		await self.db.refresh(user)
		return user

	async def authenticate_user(self, username: str, password: str) -> User | None:
		"""Authenticate a user with username and password."""
		user = await self.get_user_by_username(username)
		if not user:
			return None
		if not verify_password(password, user.hashed_password):
			return None
		return user

	async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User | None:
		"""Update a user."""
		user = await self.get_user_by_id(user_id)
		if not user:
			return None

		if user_data.username is not None:
			existing_user = await self.get_user_by_username(user_data.username)
			if existing_user and existing_user.id != user_id:
				raise ValueError("Username already exists")
			user.username = user_data.username

		if user_data.email is not None:
			existing_email = await self.get_user_by_email(user_data.email)
			if existing_email and existing_email.id != user_id:
				raise ValueError("Email already exists")
			user.email = user_data.email

		if user_data.password is not None:
			user.hashed_password = get_password_hash(user_data.password)

		if user_data.is_active is not None:
			user.is_active = user_data.is_active

		if user_data.is_admin is not None:
			user.is_admin = user_data.is_admin

		await self.db.commit()
		await self.db.refresh(user)
		return user

	async def delete_user(self, user_id: UUID) -> bool:
		"""Delete a user."""
		user = await self.get_user_by_id(user_id)
		if not user:
			return False

		await self.db.delete(user)
		await self.db.commit()
		return True
