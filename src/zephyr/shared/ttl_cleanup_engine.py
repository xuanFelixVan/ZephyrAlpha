# [A_module] module_id=MOD-SHR_ttl_cleanup_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass
class TtlEntry:
    key: str
    created_at: float
    ttl_seconds: float


@dataclass
class CleanupResult:
    expired_count: int
    remaining_count: int


class TtlCleanupEngine:
    def __init__(self, default_ttl: float = 1800.0):
        self._default_ttl = default_ttl
        self._entries: dict[str, TtlEntry] = {}

    def register(self, key: str, ttl_seconds: float | None = None) -> None:
        self._entries[key] = TtlEntry(key, time.time(), ttl_seconds or self._default_ttl)

    def is_expired(self, key: str) -> bool:
        entry = self._entries.get(key)
        if not entry:
            return True
        return (time.time() - entry.created_at) > entry.ttl_seconds

    def cleanup(self) -> CleanupResult:
        now = time.time()
        expired = [k for k, v in self._entries.items() if (now - v.created_at) > v.ttl_seconds]
        for k in expired:
            del self._entries[k]
        return CleanupResult(len(expired), len(self._entries))
