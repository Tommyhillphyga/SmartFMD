import json
from datetime import datetime

from redis.asyncio import Redis


class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    @staticmethod
    def live_pump_key(station_id: str, pump_id: str) -> str:
        return f"station:{station_id}:pump:{pump_id}:live"

    @staticmethod
    def station_summary_key(station_id: str) -> str:
        return f"station:{station_id}:summary"

    async def get_live_pump(self, station_id: str, pump_id: str) -> dict | None:
        raw = await self.redis.get(self.live_pump_key(station_id, pump_id))
        return json.loads(raw) if raw else None

    async def set_live_pump(
        self,
        station_id: str,
        pump_id: str,
        payload: dict,
        ttl_seconds: int = 3600,
    ) -> None:
        await self.redis.set(
            self.live_pump_key(station_id, pump_id),
            json.dumps(payload, default=self._json_default),
            ex=ttl_seconds,
        )

    @staticmethod
    def _json_default(value: object) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError(f"Unsupported type for cache payload: {type(value)!r}")

