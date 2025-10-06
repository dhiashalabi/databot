"""Custom exceptions for the DataBot application."""


class DataBotException(Exception):
	"""Base exception for all DataBot-related errors."""

	def __init__(
		self, message: str, error_code: str | None = None, details: dict | None = None
	):
		super().__init__(message)
		self.message = message
		self.error_code = error_code
		self.details = details or {}


class ValidationError(DataBotException):
	"""Raised when query validation fails."""

	def __init__(self, message: str, validation_errors: list[str] | None = None):
		super().__init__(message, "VALIDATION_ERROR")
		self.validation_errors = validation_errors or []


class DatabaseError(DataBotException):
	"""Raised when database operations fail."""

	def __init__(self, message: str, original_error: Exception | None = None):
		super().__init__(message, "DATABASE_ERROR")
		self.original_error = original_error


class AIError(DataBotException):
	"""Raised when AI/OpenAI operations fail."""

	def __init__(self, message: str, original_error: Exception | None = None):
		super().__init__(message, "AI_ERROR")
		self.original_error = original_error


class MCPError(DataBotException):
	"""Raised when MCP operations fail."""

	def __init__(self, message: str, original_error: Exception | None = None):
		super().__init__(message, "MCP_ERROR")
		self.original_error = original_error


class QueryProcessingError(DataBotException):
	"""Raised when query processing fails."""

	def __init__(self, message: str, original_error: Exception | None = None):
		super().__init__(message, "QUERY_PROCESSING_ERROR")
		self.original_error = original_error


class TokenLimitExceeded(DataBotException):
	"""Raised when token limits are exceeded."""

	def __init__(self, message: str, limit_type: str = "unknown"):
		super().__init__(message, "TOKEN_LIMIT_EXCEEDED")
		self.limit_type = limit_type


class ServiceConnectionError(DataBotException):
	"""Raised when connection to external services fails."""

	def __init__(self, message: str, service: str | None = None):
		super().__init__(message, "CONNECTION_ERROR")
		self.service = service


class OperationTimeoutError(DataBotException):
	"""Raised when operations timeout."""

	def __init__(self, message: str, timeout_seconds: int | None = None):
		super().__init__(message, "TIMEOUT_ERROR")
		self.timeout_seconds = timeout_seconds
