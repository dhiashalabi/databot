"""Centralized error handling and recovery mechanisms."""

from datetime import datetime
import logging
from typing import Any

from src.errors.exceptions import (
	AIError,
	DatabaseError,
	MCPError,
	OperationTimeoutError,
	QueryProcessingError,
	ServiceConnectionError,
	ValidationError,
)

logger = logging.getLogger(__name__)


class ErrorHandler:
	"""Centralized error handling and recovery for the DataBot application."""

	def __init__(self):
		"""Initialize the error handler."""
		self.error_counts = {}
		self.max_retries = 3
		self.retry_delay = 1

	def handle_error(
		self, error: Exception, context: dict[str, Any] = None
	) -> dict[str, Any]:
		"""Handle any error and return a user-friendly response.

		Args:
			error: The exception that occurred
			context: Additional context about where the error occurred

		Returns:
			Dictionary with error information for the user
		"""
		context = context or {}
		error_type = type(error).__name__

		logger.error(f"Error occurred: {error_type} - {str(error)}", extra=context)

		self._track_error(error_type)

		if isinstance(error, ValidationError):
			return self._handle_validation_error(error, context)
		elif isinstance(error, DatabaseError):
			return self._handle_database_error(error, context)
		elif isinstance(error, AIError):
			return self._handle_ai_error(error, context)
		elif isinstance(error, MCPError):
			return self._handle_mcp_error(error, context)
		elif isinstance(error, QueryProcessingError):
			return self._handle_query_processing_error(error, context)
		elif isinstance(error, ServiceConnectionError):
			return self._handle_connection_error(error, context)
		elif isinstance(error, OperationTimeoutError):
			return self._handle_timeout_error(error, context)
		else:
			return self._handle_generic_error(error, context)

	def _handle_validation_error(
		self, error: ValidationError, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle validation errors."""
		return {
			"answer": "I couldn't process your query due to validation issues. Please try rephrasing your question.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "validation_error",
				"message": error.message,
				"validation_errors": error.validation_errors,
				"suggestions": self._get_validation_suggestions(
					error.validation_errors
				),
			},
		}

	def _handle_database_error(
		self, error: DatabaseError, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle database errors."""
		return {
			"answer": "I'm having trouble accessing the database right now. Please try again in a moment.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "database_error",
				"message": "Database connection issue",
				"retry_suggested": True,
			},
		}

	def _handle_ai_error(
		self, error: AIError, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle AI/OpenAI errors."""
		return {
			"answer": "I'm having trouble processing your request with AI. Please try again or rephrase your question.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "ai_error",
				"message": "AI processing issue",
				"retry_suggested": True,
			},
		}

	def _handle_mcp_error(
		self, error: MCPError, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle MCP errors."""
		return {
			"answer": "I'm having trouble accessing my tools right now. Please try again in a moment.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "mcp_error",
				"message": "Tool access issue",
				"retry_suggested": True,
			},
		}

	def _handle_query_processing_error(
		self, error: QueryProcessingError, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle query processing errors."""
		return {
			"answer": "I couldn't process your query. Please try rephrasing it or ask something else.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "query_processing_error",
				"message": "Query processing failed",
				"suggestions": self._get_query_suggestions(),
			},
		}

	def _handle_connection_error(
		self, error: ServiceConnectionError, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle connection errors."""
		service = error.service or "external service"
		return {
			"answer": f"I'm having trouble connecting to {service}. Please try again later.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "connection_error",
				"message": f"Connection to {service} failed",
				"retry_suggested": True,
			},
		}

	def _handle_timeout_error(
		self, error: OperationTimeoutError, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle timeout errors."""
		timeout_seconds = error.timeout_seconds or "unknown"
		return {
			"answer": f"Your request timed out after {timeout_seconds} seconds. Please try a simpler query or try again.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "timeout_error",
				"message": "Request timed out",
				"retry_suggested": True,
			},
		}

	def _handle_generic_error(
		self, error: Exception, context: dict[str, Any]
	) -> dict[str, Any]:
		"""Handle generic errors."""
		return {
			"answer": "An unexpected error occurred. Please try again or contact support if the problem persists.",
			"data": None,
			"query": context.get("query", ""),
			"error": {
				"type": "generic_error",
				"message": "Unexpected error occurred",
				"retry_suggested": True,
			},
		}

	def _track_error(self, error_type: str) -> None:
		"""Track error counts for monitoring."""
		if error_type not in self.error_counts:
			self.error_counts[error_type] = 0
		self.error_counts[error_type] += 1

	def _get_validation_suggestions(self, validation_errors: list[str]) -> list[str]:
		"""Get suggestions for validation errors."""
		suggestions = []

		if any("dangerous pattern" in error.lower() for error in validation_errors):
			suggestions.append(
				"Please avoid using technical database terms in your question"
			)

		if any("sql injection" in error.lower() for error in validation_errors):
			suggestions.append("Please ask your question in plain English")

		if any("too short" in error.lower() for error in validation_errors):
			suggestions.append("Try asking a more detailed question")

		if any("too long" in error.lower() for error in validation_errors):
			suggestions.append("Try breaking your question into smaller parts")

		return suggestions

	def _get_query_suggestions(self) -> list[str]:
		"""Get general query suggestions."""
		return [
			"Try asking about sales, customers, products, or invoices",
			"Use phrases like 'show me', 'compare', 'analyze', or 'find'",
			"Be specific about time periods (e.g., 'last month', 'this year')",
			"Ask one question at a time",
		]

	def get_error_stats(self) -> dict[str, Any]:
		"""Get error statistics for monitoring."""
		return {
			"error_counts": self.error_counts.copy(),
			"total_errors": sum(self.error_counts.values()),
			"timestamp": datetime.now().isoformat(),
		}

	def should_retry(self, error: Exception, attempt: int) -> bool:
		"""Determine if an operation should be retried.

		Args:
			error: The exception that occurred
			attempt: Current attempt number (1-based)

		Returns:
			True if the operation should be retried
		"""
		if attempt >= self.max_retries:
			return False

		if isinstance(error, ValidationError):
			return False

		error_type = type(error).__name__
		if self.error_counts.get(error_type, 0) > 10:
			return False

		return True

	def get_retry_delay(self, attempt: int) -> float:
		"""Get the delay before retrying an operation.

		Args:
			attempt: Current attempt number (1-based)

		Returns:
			Delay in seconds
		"""
		return self.retry_delay * (2 ** (attempt - 1))
