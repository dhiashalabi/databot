"""User model for authentication."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class User(Base):
	"""User model for authentication."""

	__tablename__ = "user"

	id: Mapped[UUID] = mapped_column(
		PostgresUUID(as_uuid=True),
		primary_key=True,
		server_default="gen_random_uuid()",
	)
	username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
	hashed_password: Mapped[str] = mapped_column(Text, nullable=False)
	is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default="NOW()",
		nullable=False,
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default="NOW()",
		onupdate=datetime.utcnow,
		nullable=False,
	)

	def __repr__(self) -> str:
		"""String representation of the user."""
		return f"<User(id={self.id}, username={self.username}, email={self.email})>"
