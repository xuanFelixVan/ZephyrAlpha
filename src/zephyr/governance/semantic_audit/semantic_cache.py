# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.semantic_audit.semantic_cache
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
# [A_module] module_id=MOD-RES_semantic_cache | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import hashlib
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class CacheEntry:
    key: str
    response: str
    cost_saved: float
    created_at: float
    hits: int = 1


class SemanticCache:
    def __init__(self, max_entries: int = 100, ttl: float = 3600.0):
        self._max_entries = max_entries
        self._ttl = ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._total_cost_saved: float = 0.0
        self._hits: int = 0
        self._misses: int = 0
        # 5.47.2 修复：per-key single-flight 锁，防止 get miss 时 thundering herd
        self._miss_locks: dict[str, threading.Lock] = {}
        self._miss_locks_guard = threading.Lock()

    @staticmethod
    def _hash(prompt: str) -> str:
        normalized = " ".join(prompt.lower().split()[:100])
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def get(self, prompt: str) -> str | None:
        key = self._hash(prompt)
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None
        # 5.46.1 修复：time.time() 受 NTP/手动调时影响可能回退，导致 TTL 永不过期。
        # 改用 time.monotonic() 保证单调递增。
        if time.monotonic() - entry.created_at > self._ttl:
            del self._cache[key]
            self._misses += 1
            return None
        entry.hits += 1
        self._hits += 1
        self._total_cost_saved += entry.cost_saved
        self._cache.move_to_end(key)
        return entry.response

    def put(self, prompt: str, response: str, cost: float) -> None:
        key = self._hash(prompt)
        if key in self._cache:
            self._cache.move_to_end(key)
            return
        self._cache[key] = CacheEntry(key=key, response=response, cost_saved=cost, created_at=time.monotonic())
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_entries:
            self._cache.popitem(last=False)

    def get_or_compute(self, prompt: str, loader: Callable[[], tuple[str, float]]) -> str:
        """5.47.2 修复：single-flight 防止 get miss 时 thundering herd。

        cache miss 时只有一个请求穿透到 loader，其余请求等待后直接命中缓存。
        loader 返回 (response, cost) 元组。
        """
        cached = self.get(prompt)
        if cached is not None:
            return cached
        key = self._hash(prompt)
        with self._miss_locks_guard:
            lock = self._miss_locks.setdefault(key, threading.Lock())
        with lock:
            # double-check：持锁后重新检查 cache，可能已被前一个请求填充
            cached = self.get(prompt)
            if cached is not None:
                return cached
            response, cost = loader()
            self.put(prompt, response, cost)
            return response

    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total else 0.0

    def total_saved(self) -> float:
        return self._total_cost_saved

    def size(self) -> int:
        return len(self._cache)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._total_cost_saved = 0.0
        with self._miss_locks_guard:
            self._miss_locks.clear()
