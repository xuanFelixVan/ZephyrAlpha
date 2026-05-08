"""cache_invalidation.py — 缓存一致性 (DD113, TASK-020)"""
from __future__ import annotations
from datetime import datetime, timezone
from dataclasses import dataclass

UTC = timezone.utc


@dataclass
class CacheVersion:
    key: str
    version: int
    invalidated_at: str


class CacheInvalidationManager:
    """Mem/Redis 缓存 + event-driven KE update → cache invalidation (DD113)."""
    def __init__(self) -> None:
        self._versions: dict[str, CacheVersion] = {}

    def set_version(self, key: str, version: int) -> CacheVersion:
        cv = CacheVersion(key=key, version=version, invalidated_at=datetime.now(UTC).isoformat())
        self._versions[key] = cv
        return cv

    def check_staleness(self, key: str, client_version: int) -> bool:
        cv = self._versions.get(key)
        return cv is not None and cv.version > client_version
