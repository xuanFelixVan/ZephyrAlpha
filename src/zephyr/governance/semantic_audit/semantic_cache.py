# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.semantic_audit.semantic_cache
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: max_entries 参数
#   fields: 参数 max_entries（无注解）
#   code: semantic_cache.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: ttl 参数
#   fields: 参数 ttl（无注解）
#   code: semantic_cache.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SemanticCache
#   name_en: SemanticCache
#   intro: class SemanticCache 源码 L70-L152
#   desc: 公共方法（定义序）: get, put, get_or_compute, hit_rate, total_saved, size, clear；源码 L70-L152
#   inputs: max_entries ttl
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SemanticCache
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

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
