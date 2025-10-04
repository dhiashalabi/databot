"""Generic fuzzy search utilities for efficient and secure text matching."""

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def calculate_similarity(str1: str, str2: str) -> float:
	"""
	Calculate simple similarity between two strings.

	Args:
		str1: First string to compare
		str2: Second string to compare

	Returns:
		Similarity score between 0.0 (no match) and 1.0 (exact match)
	"""
	if not str1 or not str2:
		return 0.0

	str1 = str1.lower().strip()
	str2 = str2.lower().strip()

	if str1 == str2:
		return 1.0

	if str1 in str2 or str2 in str1:
		return 0.8

	words1 = set(str1.split())
	words2 = set(str2.split())
	common_words = words1.intersection(words2)

	if common_words:
		return len(common_words) / max(len(words1), len(words2))

	chars1 = set(str1.replace(" ", ""))
	chars2 = set(str2.replace(" ", ""))
	common_chars = chars1.intersection(chars2)

	if common_chars:
		return len(common_chars) / max(len(chars1), len(chars2))

	return 0.0


def find_fuzzy_matches(
	search_term: str, candidates: list[str], threshold: float = 0.5
) -> list[tuple[str, float]]:
	"""
	Find fuzzy matches for a search term from a list of candidates.

	Args:
		search_term: The term to search for
		candidates: List of candidate strings to search through
		threshold: Minimum similarity score to include (0.0 to 1.0)

	Returns:
		List of tuples (candidate, similarity_score) sorted by similarity (highest first)
	"""
	matches = []
	search_term = search_term.lower().strip()

	for candidate in candidates:
		similarity = calculate_similarity(search_term, candidate)
		if similarity >= threshold:
			matches.append((candidate, similarity))

	matches.sort(key=lambda x: x[1], reverse=True)
	return matches


def fuzzy_search_objects(
	search_term: str,
	objects: list[T],
	text_extractor: Callable[[T], str],
	threshold: float = 0.5,
	limit: int | None = None,
) -> list[tuple[T, float]]:
	"""
	Find fuzzy matches in a list of objects using a text extractor function.

	Args:
		search_term: The term to search for
		objects: List of objects to search through
		text_extractor: Function that extracts searchable text from each object
		threshold: Minimum similarity score to include (0.0 to 1.0)
		limit: Maximum number of results to return (None for all)

	Returns:
		List of tuples (object, similarity_score) sorted by similarity (highest first)
	"""
	matches = []
	search_term = search_term.lower().strip()

	for obj in objects:
		text = text_extractor(obj)
		if not text:
			continue

		similarity = calculate_similarity(search_term, text)
		if similarity >= threshold:
			matches.append((obj, similarity))

	matches.sort(key=lambda x: x[1], reverse=True)

	if limit is not None:
		matches = matches[:limit]

	return matches


def sanitize_search_term(search_term: str) -> str:
	"""
	Sanitize search term for security and consistency.

	Args:
		search_term: Raw search term from user input

	Returns:
		Sanitized search term safe for processing
	"""
	if not search_term:
		return ""

	sanitized = search_term.strip()

	if len(sanitized) > 100:
		sanitized = sanitized[:100]

	return sanitized
