"""Permission models for role-based access control."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
	from src.models.user import User


class Role(Base):
	"""Role model for permission system."""

	__tablename__ = "roles"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default="NOW()",
		nullable=False,
	)

	permissions: Mapped[list["Permission"]] = relationship(
		"Permission", secondary="role_permissions", back_populates="roles"
	)
	users: Mapped[list["User"]] = relationship(
		"User", secondary="user_roles", back_populates="roles"
	)

	def __repr__(self) -> str:
		"""String representation of the role."""
		return f"<Role(id={self.id}, name={self.name})>"


class Permission(Base):
	"""Permission model for access control."""

	__tablename__ = "permissions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
	description: Mapped[str | None] = mapped_column(Text, nullable=True)
	category: Mapped[str | None] = mapped_column(String(50), nullable=True)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default="NOW()",
		nullable=False,
	)

	roles: Mapped[list["Role"]] = relationship(
		"Role", secondary="role_permissions", back_populates="permissions"
	)

	def __repr__(self) -> str:
		"""String representation of the permission."""
		return f"<Permission(id={self.id}, code={self.code})>"


class RolePermission(Base):
	"""Association table for roles and permissions."""

	__tablename__ = "role_permissions"

	role_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
	)
	permission_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
	)


class UserRole(Base):
	"""Association table for users and roles."""

	__tablename__ = "user_roles"

	user_id: Mapped[UUID] = mapped_column(
		PostgresUUID(as_uuid=True),
		ForeignKey("user.id", ondelete="CASCADE"),
		primary_key=True,
	)
	role_id: Mapped[int] = mapped_column(
		Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
	)


class ToolPermission(Base):
	"""Tool-specific permission mapping."""

	__tablename__ = "tool_permissions"

	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
	permission_code: Mapped[str] = mapped_column(
		String(100), ForeignKey("permissions.code"), nullable=False
	)
	is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default="NOW()",
		nullable=False,
	)

	def __repr__(self) -> str:
		"""String representation of the tool permission."""
		return f"<ToolPermission(tool_name={self.tool_name}, permission_code={self.permission_code})>"
