# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.io_cache
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.lifecycle.resource_optimization_models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_io_cache | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
io_cache.py - File-level I/O cache with LRU eviction
=====================================================

SSoT: MOD-RESOURCE_OPTIMIZATION_ENGINE resource-optimization-engine/blueprint.md §11 Phase 2

Design:
  - Cache key = (file_path, mtime) → file changes auto-invalidate
  - LRU eviction when max_entries reached
  - Supports YAML and JSON files
  - Memory usage tracking
  - Warm-up for preloading hot files
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from zephyr.shared.lifecycle.resource_optimization_models import CacheStats

__all__ = ["FileCache"]

logger = logging.getLogger(__name__)


class _CacheEntry:
    __slots__ = ("access_time", "data", "mtime", "size_bytes")

    def __init__(self, data: Any, size_bytes: int, mtime: float) -> None:
        self.data = data
        self.size_bytes = size_bytes
        self.mtime = mtime
        self.access_time = time.monotonic()


class FileCache:
    def __init__(
        self,
        max_entries: int = 1000,
        ttl_seconds: float = 300.0,
    ) -> None:
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._entries: OrderedDict[str, _CacheEntry] = OrderedDict()
        self._hit_count = 0
        self._miss_count = 0
        self._evictions = 0
        self._lock = threading.Lock()

    def get(self, file_path: str | Path) -> dict | list | None:
        path = str(Path(file_path).resolve())
        with self._lock:
            entry = self._entries.get(path)
            if entry is not None:
                try:
                    current_mtime = os.path.getmtime(path)
                except OSError:
                    self._remove_entry(path)
                    self._miss_count += 1
                    return None
                if current_mtime != entry.mtime:
                    self._remove_entry(path)
                    self._miss_count += 1
                    return None
                if time.monotonic() - entry.access_time > self._ttl_seconds:
                    self._remove_entry(path)
                    self._miss_count += 1
                    return None
                entry.access_time = time.monotonic()
                self._entries.move_to_end(path)
                self._hit_count += 1
                return entry.data
            self._miss_count += 1
            return None

    def get_or_load(self, file_path: str | Path) -> dict | list | None:
        path = str(Path(file_path).resolve())
        cached = self.get(path)
        if cached is not None:
            return cached
        return self._load_and_cache(path)

    def invalidate(self, file_path: str | Path) -> bool:
        path = str(Path(file_path).resolve())
        with self._lock:
            if path in self._entries:
                self._remove_entry(path)
                return True
            return False

    def warm(self, file_paths: list[str | Path]) -> int:
        loaded = 0
        for fp in file_paths:
            try:
                result = self._load_and_cache(str(Path(fp).resolve()))
                if result is not None:
                    loaded += 1
            except Exception:
                logger.debug("FileCache: warm failed for %s", fp, exc_info=True)
        return loaded

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._hit_count = 0
            self._miss_count = 0
            self._evictions = 0

    def get_stats(self) -> CacheStats:
        from zephyr.shared.lifecycle.resource_optimization_models import CacheStats as _CacheStats

        with self._lock:
            total = self._hit_count + self._miss_count
            hit_rate = self._hit_count / total if total > 0 else 0.0
            memory_mb = sum(e.size_bytes for e in self._entries.values()) / (1024 * 1024)
            return _CacheStats(
                total_entries=len(self._entries),
                hit_count=self._hit_count,
                miss_count=self._miss_count,
                hit_rate=round(hit_rate, 4),
                memory_usage_mb=round(memory_mb, 2),
                evictions=self._evictions,
            )

    def _load_and_cache(self, path: str) -> dict | list | None:
        if not os.path.isfile(path):
            return None
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            return None
        try:
            with open(path, encoding="utf-8") as f:
                raw = f.read()
            if path.endswith((".yaml", ".yml")):
                data = yaml.safe_load(raw)
            elif path.endswith(".json"):
                data = json.loads(raw)
            else:
                data = yaml.safe_load(raw) or json.loads(raw)
            size_bytes = len(raw.encode("utf-8"))
        except Exception:
            logger.debug("FileCache: parse failed for %s", path, exc_info=True)
            return None
        if data is None:
            return None
        with self._lock:
            if path in self._entries:
                self._remove_entry(path)
            while len(self._entries) >= self._max_entries:
                self._evict_one()
            self._entries[path] = _CacheEntry(data, size_bytes, mtime)
        return data

    def _evict_one(self) -> None:
        if self._entries:
            self._entries.popitem(last=False)
            self._evictions += 1

    def _remove_entry(self, path: str) -> None:
        self._entries.pop(path, None)