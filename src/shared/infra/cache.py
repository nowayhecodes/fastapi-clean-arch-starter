import json
from typing import Any

from redis import ConnectionPool, Redis

from src.shared.infra.config import settings


class CacheManager:
    def __init__(self):
        self.pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            max_connections=20,
            decode_responses=True,
        )
        self.redis = Redis(connection_pool=self.pool)

    async def get(self, key: str) -> Any | None:
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, expire: int = 3600) -> None:
        self.redis.setex(key, expire, json.dumps(value))

    async def delete(self, key: str) -> None:
        self.redis.delete(key)

    async def clear_pattern(self, pattern: str) -> None:
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)


cache_manager = CacheManager()
