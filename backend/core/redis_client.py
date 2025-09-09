"""Redis client configuration and utilities for the news app."""

import json
import os
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from redis import Redis

import redis
import structlog

logger = structlog.get_logger()


class RedisClient:
    """Redis client wrapper for daily limits and caching."""

    _instance = None
    _client = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Redis client with configuration from environment."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        logger.info(f"Initializing Redis client with URL: {redis_url}")

        self._client = redis.from_url(
            redis_url,
            decode_responses=True,  # Automatically decode bytes to strings
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )

        # Test connection - will raise exception if Redis is not available
        self._client.ping()
        logger.info(f"Redis client connected successfully to {redis_url}")

    @property
    def client(self) -> "Redis[str]":
        """Get the Redis client instance."""
        if self._client is None:
            self._initialize_client()
        assert self._client is not None
        return self._client

    def set_daily_limit(self, key: str, data: dict[str, Any], ttl: int = 86400) -> bool:
        """
        Set a daily limit key with data and TTL (time to live).

        Args:
            key: The cache key
            data: Dictionary of data to store
            ttl: Time to live in seconds (default: 24 hours = 86400)

        Returns:
            True if successful, False otherwise
        """
        result = self.client.setex(key, ttl, json.dumps(data))
        return bool(result)

    def has_daily_limit(self, key: str) -> bool:
        """
        Check if a daily limit key exists.

        Args:
            key: The cache key to check

        Returns:
            True if key exists, False otherwise
        """
        return bool(self.client.exists(key))

    def get_daily_limit(self, key: str) -> Any | None:
        """
        Get daily limit data by key.

        Args:
            key: The cache key

        Returns:
            JSON data if found, None otherwise
        """
        data = self.client.get(key)
        if data:
            return json.loads(str(data))
        return None

    def delete_daily_limit(self, key: str) -> bool:
        """
        Delete a daily limit key.

        Args:
            key: The cache key to delete

        Returns:
            True if key was deleted, False otherwise
        """
        return bool(self.client.delete(key))

    def increment_counter(self, key: str, ttl: int = 86400) -> int:
        """
        Increment a counter with automatic expiry.

        Args:
            key: The counter key
            ttl: Time to live in seconds (default: 24 hours = 86400)

        Returns:
            Current count after increment
        """
        pipe = self.client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl)
        results = pipe.execute()
        return int(results[0])

    def get_counter(self, key: str) -> int:
        """
        Get current counter value.

        Args:
            key: The counter key

        Returns:
            Current count (0 if key doesn't exist)
        """
        count = self.client.get(key)
        return int(str(count)) if count else 0


# Global Redis client instance
redis_client = RedisClient()
