# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_cache_provider
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_cache_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Cache Provider
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 缓存供应商——多后端缓存切换
================================
Memory + Disk 双后端，自动 fallback
"""

from __future__ import annotations

import json
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any


class _MemoryCache:
    def __init__(self, max_size: int = 100):
        self._max = max_size
        self._store: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str):  # noqa: ANN
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
                return self._store[key]
        return None

    def set(self, key: str, value: Any):
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = value
            if len(self._store) > self._max:
                self._store.popitem(last=False)

    def invalidate(self, key: str):
        with self._lock:
            self._store.pop(key, None)

    def clear(self):
        with self._lock:
            self._store.clear()


class _DiskCache:
    def __init__(self, cache_dir: Path | None = None):
        self._dir = cache_dir or (Path(__file__).resolve().parent / "_skill_cache")
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = key.replace(":", "_").replace("/", "_").replace("\\", "_")[:200]
        return self._dir / f"{safe}.json"

    def get(self, key: str):  # noqa: ANN
        path = self._path(key)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("expires_at", 0) > time.time():
                    return data.get("value")
            except (OSError, json.JSONDecodeError):
                pass
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        data = {"value": value, "expires_at": time.time() + ttl_seconds}
        try:
            self._path(key).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass

    def invalidate(self, key: str):
        try:
            self._path(key).unlink(missing_ok=True)
        except Exception:
            pass


class SkillCacheProvider:
    _BACKENDS = ["memory", "disk"]

    def __init__(self, backend: str = "memory"):
        self._backend_name = "memory"
        self.__backend = None
        self.configure(backend)

    def configure(self, backend: str) -> dict[str, Any]:
        avail = backend.lower().strip() in self._BACKENDS
        if backend.lower().strip() == "disk" and avail:
            self.__backend = _DiskCache()
            self._backend_name = "disk"
        else:
            self.__backend = _MemoryCache()
            self._backend_name = "memory"
        return {"backend": self._backend_name, "requested": backend, "available": avail}

    def get(self, key: str):  # noqa: ANN
        if self.__backend is None:
            self.__backend = _MemoryCache()
        return self.__backend.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        if self.__backend is None:
            self.__backend = _MemoryCache()
        if isinstance(self.__backend, _DiskCache):
            self.__backend.set(key, value, ttl_seconds)
        else:
            self.__backend.set(key, value)

    def invalidate(self, key: str):
        if self.__backend:
            self.__backend.invalidate(key)

    def clear(self):
        if self.__backend:
            self.__backend.clear()
