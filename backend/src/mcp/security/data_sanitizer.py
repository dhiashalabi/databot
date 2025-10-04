"""Data sanitization for sensitive information."""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class DataSanitizer:
	"""Sanitizes sensitive data before returning to clients."""

	def __init__(self):
		"""Initialize the data sanitizer."""
		self.email_pattern = re.compile(
			r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
		)
		self.phone_pattern = re.compile(
			r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3,4})([-.\s]?([0-9]{4}))?(?!\w)"
		)
		self.ssn_pattern = re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b")
		self.credit_card_pattern = re.compile(
			r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
		)
		self.url_pattern = re.compile(r"(https?://|/static/|/api/|/assets/)[^\s]+")

		self.sensitive_fields = {
			"email",
			"phone",
			"phone_number",
			"mobile",
			"telephone",
			"ssn",
			"social_security",
			"credit_card",
			"card_number",
			"address",
			"street_address",
			"billing_address",
			"password",
			"secret",
			"token",
			"api_key",
		}

		self.url_fields = {
			"url",
			"link",
			"href",
			"src",
			"chart_url",
			"image_url",
			"file_url",
			"download_url",
			"redirect_url",
		}

	def sanitize_data(self, data: Any) -> Any:
		"""Sanitize sensitive data in any data structure."""
		if isinstance(data, dict):
			return self._sanitize_dict(data)
		elif isinstance(data, list):
			return [self.sanitize_data(item) for item in data]
		elif isinstance(data, str):
			return self._sanitize_string(data)
		else:
			return data

	def _sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
		"""Sanitize sensitive fields in a dictionary."""
		sanitized = {}

		for key, value in data.items():
			if any(url_field in key.lower() for url_field in self.url_fields):
				sanitized[key] = value
			elif any(sensitive in key.lower() for sensitive in self.sensitive_fields):
				sanitized[key] = self._mask_sensitive_field(key, value)
			else:
				sanitized[key] = self.sanitize_data(value)

		return sanitized

	def _sanitize_string(self, text: str) -> str:
		"""Sanitize sensitive patterns in a string."""
		if not isinstance(text, str):
			return text

		if self.url_pattern.search(text):
			return text

		text = self.email_pattern.sub(self._mask_email, text)
		text = self.phone_pattern.sub(self._mask_phone, text)
		text = self.ssn_pattern.sub("***-**-****", text)
		text = self.credit_card_pattern.sub("****-****-****-****", text)

		return text

	def _mask_sensitive_field(self, field_name: str, value: Any) -> str:
		"""Mask a sensitive field based on its type."""
		if not value or value == "":
			return value

		if isinstance(value, str):
			if "email" in field_name.lower():
				return self._mask_email(value)
			elif any(
				phone in field_name.lower()
				for phone in ["phone", "mobile", "telephone"]
			):
				return self._mask_phone_string(value)
			elif "ssn" in field_name.lower() or "social" in field_name.lower():
				return "***-**-****"
			elif any(
				card in field_name.lower() for card in ["credit", "card", "payment"]
			):
				return "****-****-****-****"
			else:
				return self._mask_generic(value)
		else:
			return "***MASKED***"

	def _mask_email(self, email: str) -> str:
		"""Mask email address showing only first 3 characters."""
		if "@" not in email:
			return email

		local, domain = email.split("@", 1)
		if len(local) <= 3:
			return f"{local[0]}***@{domain}"
		else:
			return f"{local[:3]}***@{domain}"

	def _mask_phone(self, match) -> str:
		"""Mask phone number showing only last 4 digits."""
		phone = match.group(0)
		digits = re.sub(r"\D", "", phone)
		if len(digits) >= 4:
			return f"XXX-XXX-{digits[-4:]}"
		else:
			return "XXX-XXX-XXXX"

	def _mask_phone_string(self, phone: str) -> str:
		"""Mask phone number string (for dictionary fields)."""
		digits = re.sub(r"\D", "", phone)
		if len(digits) >= 4:
			return f"XXX-XXX-{digits[-4:]}"
		else:
			return "XXX-XXX-XXXX"

	def _mask_generic(self, value: str) -> str:
		"""Generic masking for other sensitive fields."""
		if len(value) <= 3:
			return "***"
		else:
			return f"{value[:3]}***"

	def sanitize_customer_data(self, customer: dict[str, Any]) -> dict[str, Any]:
		"""Sanitize customer data specifically."""
		sanitized = customer.copy()

		customer_sensitive = [
			"email",
			"phone",
			"phone_number",
			"address",
			"billing_address",
		]

		for field in customer_sensitive:
			if field in sanitized and sanitized[field]:
				sanitized[field] = self._mask_sensitive_field(field, sanitized[field])

		return sanitized

	def sanitize_sales_data(
		self, sales_data: dict[str, Any] | list[dict[str, Any]]
	) -> dict[str, Any] | list[dict[str, Any]]:
		"""Sanitize sales data (usually less sensitive but check for customer info)."""
		if isinstance(sales_data, list):
			return [self.sanitize_data(sale) for sale in sales_data]
		else:
			return self.sanitize_data(sales_data)

	def is_sensitive_field(self, field_name: str) -> bool:
		"""Check if a field name suggests sensitive data."""
		return any(
			sensitive in field_name.lower() for sensitive in self.sensitive_fields
		)
