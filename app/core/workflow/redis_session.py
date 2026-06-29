import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import redis

from core.config import settings

logger = logging.getLogger(__name__)

RESET_KEYWORDS = {"Bonjour Afiya", "restart", "menu", "0", "stop"}


class RedisSessionStore:
    def __init__(self, ttl_hours: int = 48):
        self.r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _key(self, wa_id: str) -> str:
        return f"session:{wa_id}:context"

    def get(self, wa_id: str) -> Optional[dict]:
        raw = self.r.hgetall(self._key(wa_id))
        if not raw:
            return None
        return {k: self._deserialize(v) for k, v in raw.items()}

    def get_field(self, wa_id: str, field: str):
        val = self.r.hget(self._key(wa_id), field)
        return self._deserialize(val) if val else None

    def exists(self, wa_id: str) -> bool:
        return bool(self.r.exists(self._key(wa_id)))

    def set_field(self, wa_id: str, field: str, value) -> None:
        self.r.hset(self._key(wa_id), field, self._serialize(value))
        self.r.expire(self._key(wa_id), int(self.ttl.total_seconds()))

    def set_fields(self, wa_id: str, fields: dict) -> None:
        serialized = {k: self._serialize(v) for k, v in fields.items()}
        self.r.hset(self._key(wa_id), mapping=serialized)
        self.r.expire(self._key(wa_id), int(self.ttl.total_seconds()))

    def init(self, wa_id: str, initial_data: dict) -> None:
        self.r.delete(self._key(wa_id))
        self.set_fields(wa_id, initial_data)
        logger.info("[REDIS] Session initialisee : %s | TTL=%sh", wa_id, self.ttl.seconds // 3600)

    def delete(self, wa_id: str) -> None:
        self.r.delete(self._key(wa_id))
        logger.info("[REDIS] Session supprimee : %s", wa_id)

    def set_ttl(self, hours: int) -> None:
        self.ttl = timedelta(hours=hours)

    @staticmethod
    def _serialize(value) -> str:
        return json.dumps(value, default=str)

    @staticmethod
    def _deserialize(value):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
