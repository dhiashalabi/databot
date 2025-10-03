"""Query validation and sanitization for user inputs."""

import re

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
	"""Result of query validation."""

	is_valid: bool
	sanitized_query: str
	errors: list[str] = Field(default_factory=list)
	warnings: list[str] = Field(default_factory=list)


class QueryValidator:
	"""Validates and sanitizes user queries for security and correctness."""

	def __init__(self):
		"""Initialize the validator with security patterns."""
		self.dangerous_patterns = [
			r"drop\s+table",
			r"delete\s+from",
			r"truncate\s+table",
			r"alter\s+table",
			r"create\s+table",
			r"insert\s+into",
			r"update\s+set",
			r"exec\s*\(",
			r"execute\s*\(",
			r"script\s*>",
			r"<script",
			r"javascript:",
			r"onload\s*=",
			r"onerror\s*=",
			r"union\s+select",
			r"or\s+1\s*=\s*1",
			r"'\s*or\s*'",
			r"\"\s*or\s*\"",
		]

		self.sql_injection_patterns = [
			r"'\s*;\s*--",
			r"'\s*;\s*drop",
			r"'\s*;\s*delete",
			r"'\s*;\s*insert",
			r"'\s*;\s*update",
			r"'\s*;\s*truncate",
			r"'\s*;\s*alter",
			r"'\s*;\s*create",
			r"'\s*;\s*exec",
			r"'\s*;\s*execute",
			r"'\s*;\s*union",
			r"'\s*;\s*select",
		]

		self.max_query_length = 2000
		self.min_query_length = 1

	def validate_query(self, query: str) -> ValidationResult:
		"""Validate a user query for security and correctness.

		Args:
			query: The user's natural language query

		Returns:
			ValidationResult with validation status and sanitized query
		"""
		errors = []
		warnings = []

		if not query or not query.strip():
			errors.append("Query cannot be empty.")
			return ValidationResult(is_valid=False, sanitized_query="", errors=errors)

		sanitized_query = self.sanitize_query(query)

		if len(query) > self.max_query_length:
			errors.append(
				f"Query too long. Maximum {self.max_query_length} characters allowed."
			)
			return ValidationResult(
				is_valid=False, sanitized_query=sanitized_query, errors=errors
			)

		dangerous_found = self._check_dangerous_patterns(sanitized_query)
		if dangerous_found:
			errors.extend(dangerous_found)

		sql_injection_found = self._check_sql_injection_patterns(sanitized_query)
		if sql_injection_found:
			errors.extend(sql_injection_found)

		suspicious_chars = self._check_suspicious_characters(sanitized_query)
		if suspicious_chars:
			warnings.extend(suspicious_chars)

		is_valid = len(errors) == 0

		return ValidationResult(
			is_valid=is_valid,
			sanitized_query=sanitized_query,
			errors=errors,
			warnings=warnings,
		)

	def sanitize_query(self, query: str) -> str:
		"""Sanitize a query by removing or escaping potentially harmful content.

		Args:
			query: The original query

		Returns:
			Sanitized query string
		"""
		if not query:
			return ""

		sanitized = query.replace("\x00", "")

		sanitized = re.sub(r"\s+", " ", sanitized)

		sanitized = re.sub(r"<[^>]*>", "", sanitized)

		sanitized = re.sub(
			r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL
		)

		sanitized = re.sub(r"--.*$", "", sanitized, flags=re.MULTILINE)
		sanitized = re.sub(r"/\*.*?\*/", "", sanitized, flags=re.DOTALL)

		sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)

		sanitized = sanitized.strip()

		return sanitized

	def _check_dangerous_patterns(self, query: str) -> list[str]:
		"""Check for dangerous patterns in the query."""
		errors = []
		query_lower = query.lower()

		for pattern in self.dangerous_patterns:
			if re.search(pattern, query_lower, re.IGNORECASE):
				errors.append(
					f"Query contains potentially dangerous pattern: {pattern}"
				)

		return errors

	def _check_sql_injection_patterns(self, query: str) -> list[str]:
		"""Check for SQL injection patterns in the query."""
		errors = []
		query_lower = query.lower()

		for pattern in self.sql_injection_patterns:
			if re.search(pattern, query_lower, re.IGNORECASE):
				errors.append(
					f"Query contains potential SQL injection pattern: {pattern}"
				)

		return errors

	def _check_suspicious_characters(self, query: str) -> list[str]:
		"""Check for suspicious characters in the query."""
		warnings = []

		special_char_count = len(re.findall(r"[^\w\s]", query))
		total_chars = len(query)

		if total_chars > 0 and special_char_count / total_chars > 0.5:
			warnings.append("Query contains many special characters")

		if re.search(r"(.)\1{10,}", query):
			warnings.append("Query contains excessive repeated characters")

		return warnings

	def get_suggestions(self, query: str) -> list[str]:
		"""Get suggestions for improving a query.

		Args:
			query: The user's query

		Returns:
			List of suggestions for better queries
		"""
		suggestions = []

		if len(query) < 10:
			suggestions.append("Try asking a more specific question")

		if not any(
			word in query.lower()
			for word in ["sales", "customer", "product", "invoice", "revenue", "profit"]
		):
			suggestions.append(
				"Try asking about sales, customers, products, or invoices"
			)

		if not any(
			word in query.lower()
			for word in ["show", "get", "find", "list", "compare", "analyze"]
		):
			suggestions.append(
				"Try starting with words like 'show', 'get', 'find', 'list', 'compare', or 'analyze'"
			)

		return suggestions
