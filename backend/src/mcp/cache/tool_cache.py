"""Tool result caching for performance optimization."""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ToolCache:
	"""In-memory cache for tool results with TTL support."""

	def __init__(self, default_ttl: int = 300, max_size: int = 1000):
		"""Initialize the tool cache.

		Args:
			default_ttl: Default time-to-live in seconds (5 minutes)
			max_size: Maximum number of cached items
		"""
		self.default_ttl = default_ttl
		self.max_size = max_size
		self._cache: dict[str, dict[str, Any]] = {}
		self._access_times: dict[str, float] = {}
		self._lock = asyncio.Lock()

	def _generate_key(self, tool_name: str, arguments: dict[str, Any]) -> str:
		"""Generate a cache key from tool name and arguments."""
		sorted_args = json.dumps(arguments, sort_keys=True, default=str)
		key_data = f"{tool_name}:{sorted_args}"
		return hashlib.md5(key_data.encode()).hexdigest()

	def _is_expired(self, key: str, ttl: int) -> bool:
		"""Check if a cache entry is expired."""
		if key not in self._cache:
			return True

		entry_time = self._cache[key].get("timestamp", 0)
		return time.time() - entry_time > ttl

	def _evict_lru(self) -> None:
		"""Evict least recently used entries if cache is full."""
		if len(self._cache) < self.max_size:
			return

		sorted_items = sorted(self._access_times.items(), key=lambda x: x[1])
		to_remove = int(self.max_size * 0.1) or 1

		for key, _ in sorted_items[:to_remove]:
			self._cache.pop(key, None)
			self._access_times.pop(key, None)

	async def get(
		self, tool_name: str, arguments: dict[str, Any], ttl: int | None = None
	) -> Any | None:
		"""Get cached result for a tool call.

		Args:
			tool_name: Name of the tool
			arguments: Tool arguments
			ttl: Time-to-live override (uses default if None)

		Returns:
			Cached result or None if not found/expired
		"""
		async with self._lock:
			key = self._generate_key(tool_name, arguments)
			cache_ttl = ttl or self.default_ttl

			if key in self._cache and not self._is_expired(key, cache_ttl):
				self._access_times[key] = time.time()
				logger.debug(f"Cache hit for tool: {tool_name}")
				return self._cache[key]["result"]

			if key in self._cache:
				self._cache.pop(key, None)
				self._access_times.pop(key, None)

			logger.debug(f"Cache miss for tool: {tool_name}")
			return None

	async def set(
		self,
		tool_name: str,
		arguments: dict[str, Any],
		result: Any,
		ttl: int | None = None,
	) -> None:
		"""Cache a tool result.

		Args:
			tool_name: Name of the tool
			arguments: Tool arguments
			result: Tool result to cache
			ttl: Time-to-live override (uses default if None)
		"""
		async with self._lock:
			key = self._generate_key(tool_name, arguments)
			cache_ttl = ttl or self.default_ttl

			self._evict_lru()

			self._cache[key] = {
				"result": result,
				"timestamp": time.time(),
				"ttl": cache_ttl,
				"tool_name": tool_name,
			}
			self._access_times[key] = time.time()

			logger.debug(f"Cached result for tool: {tool_name}")

	async def invalidate_tool(self, tool_name: str) -> None:
		"""Invalidate all cache entries for a specific tool.

		Args:
			tool_name: Name of the tool to invalidate
		"""
		async with self._lock:
			keys_to_remove = [
				key
				for key, entry in self._cache.items()
				if entry.get("tool_name") == tool_name
			]

			for key in keys_to_remove:
				self._cache.pop(key, None)
				self._access_times.pop(key, None)

	async def invalidate_all(self) -> None:
		"""Invalidate all cache entries."""
		async with self._lock:
			self._cache.clear()
			self._access_times.clear()

	async def cleanup_expired(self) -> None:
		"""Remove all expired entries from cache."""
		async with self._lock:
			current_time = time.time()
			expired_keys = []

			for key, entry in self._cache.items():
				ttl = entry.get("ttl", self.default_ttl)
				if current_time - entry.get("timestamp", 0) > ttl:
					expired_keys.append(key)

			for key in expired_keys:
				self._cache.pop(key, None)
				self._access_times.pop(key, None)

			if expired_keys:
				logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

	def get_stats(self) -> dict[str, Any]:
		"""Get cache statistics."""
		current_time = time.time()
		expired_count = 0

		for entry in self._cache.values():
			ttl = entry.get("ttl", self.default_ttl)
			if current_time - entry.get("timestamp", 0) > ttl:
				expired_count += 1

		return {
			"total_entries": len(self._cache),
			"expired_entries": expired_count,
			"active_entries": len(self._cache) - expired_count,
			"max_size": self.max_size,
			"default_ttl": self.default_ttl,
		}

	async def start_cleanup_task(self, interval: int = 60) -> None:
		"""Start background cleanup task.

		Args:
			interval: Cleanup interval in seconds
		"""

		async def cleanup_loop():
			while True:
				try:
					await self.cleanup_expired()
					await asyncio.sleep(interval)
				except Exception as e:
					logger.error(f"Cache cleanup error: {e}")
					await asyncio.sleep(interval)

		asyncio.create_task(cleanup_loop())
