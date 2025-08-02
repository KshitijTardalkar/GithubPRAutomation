from typing import Optional, Dict, Any
import json
import redis


class RedisCacheService:
    """
    Handles getting and setting data in a Redis cache.
    """
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 1):
        """
        Initializes the Redis client.
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True  # Decode responses to UTF-8
            )
            # Test the connection
            self.redis_client.ping()
            print("Successfully connected to Redis, on database number {db}.".format(db=db))
        except redis.exceptions.ConnectionError as e:
            print(f"Error connecting to Redis, on database number {db}: {e}")
            self.redis_client = None


    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Gets a value from the cache and decodes it from JSON.
        """
        if not self.redis_client:
            return None
        try:
            cached_value = self.redis_client.get(key)
            if not cached_value:
                return None
            # The value in Redis is a JSON string, so we parse it back to a dict
            return json.loads(cached_value)
        except (json.JSONDecodeError, KeyError, TypeError):
            print(f"[REDIS] Cache data for key '{key}' is corrupt or malformed.")
            return None

    def set(self, key: str, value: Dict[str, Any], expiry_seconds: int = 3600):
        """
        Encodes a value to JSON and sets it in the cache with an expiry.
        """
        if not self.redis_client:
            return
        # Convert the Python dict to a JSON string before storing
        self.redis_client.set(key, json.dumps(value), ex=expiry_seconds)