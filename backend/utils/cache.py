"""
Scalable Caching Utilities
- Uses Redis if REDIS_URL is set (Production)
- Falls back to in-memory dictionary (Local Development)
"""
import os
import json
import logging
from typing import Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Global cache store for local fallback
_local_cache = {}

class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.use_redis = False
        
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                self.use_redis = True
                logger.info("✅ [Cache] Connected to Redis.")
            except Exception as e:
                logger.warning(f"⚠️ [Cache] Redis defined but connection failed: {e}. using local fallback.")
        else:
            logger.info("ℹ️ [Cache] No REDIS_URL found. Using local in-memory cache.")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache."""
        try:
            if self.use_redis:
                val = self.redis_client.get(key)
                return json.loads(val) if val else None
            else:
                return _local_cache.get(key)
        except Exception as e:
            logger.error(f"❌ [Cache] Error getting key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set a value in cache with TTL."""
        try:
            serialized = json.dumps(value)
            if self.use_redis:
                self.redis_client.setex(key, ttl_seconds, serialized)
            else:
                # Basic local implementation (TTL ignored for simplicity in pure dict)
                _local_cache[key] = value
        except Exception as e:
            logger.error(f"❌ [Cache] Error setting key {key}: {e}")

    def delete(self, key: str):
        """Remove a value from cache."""
        try:
            if self.use_redis:
                self.redis_client.delete(key)
            else:
                if key in _local_cache:
                    del _local_cache[key]
        except Exception as e:
            logger.error(f"❌ [Cache] Error deleting key {key}: {e}")

    def flush(self):
        """Clear all cache."""
        if self.use_redis:
            self.redis_client.flushdb()
        else:
            _local_cache.clear()

# Singleton instance
cache = CacheManager()
