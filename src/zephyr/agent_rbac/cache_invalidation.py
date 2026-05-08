"""缓存一致性推送——推送驱动失效(max_latency=100ms) + 降级攻击防护."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class CacheInvalidationEvent(BaseModel):
    event_id: str
    rule_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    max_latency_ms: int = 100
    processed: bool = False


class CacheInvalidation:
    def __init__(self) -> None:
        self._events: list[CacheInvalidationEvent] = []
        self._degraded: bool = False
        self._recovered: bool = False

    def push_invalidation(self, rule_id: str) -> CacheInvalidationEvent:
        event = CacheInvalidationEvent(
            event_id=f"CACHE-INV-{rule_id}-{__import__('secrets').token_hex(4)}",
            rule_id=rule_id,
        )
        self._events.append(event)
        return event

    def process(self, event_id: str) -> dict[str, Any]:
        for ev in self._events:
            if ev.event_id == event_id:
                ev.processed = True
                return {"processed": True, "event_id": event_id, "rule_id": ev.rule_id}
        return {"processed": False, "reason": "event_not_found", "event_id": event_id}

    def detect_degradation(self, stale_count: int, threshold: int = 50) -> dict[str, Any]:
        if stale_count > threshold:
            self._degraded = True
            return {"degraded": True, "stale_count": stale_count, "threshold": threshold, "action": "cut_degraded_stream"}
        self._degraded = False
        return {"degraded": False, "stale_count": stale_count}

    @property
    def is_healthy(self) -> bool:
        return not self._degraded
