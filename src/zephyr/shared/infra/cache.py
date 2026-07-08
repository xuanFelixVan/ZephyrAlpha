# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.cache
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] orchestration.context_management.context_budget_tracker
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_cache | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
cache.py —— 统一缓存抽象（Phase 8 新增 | 盲点 B13 修复）

痛点修复：LLM API 响应、因子计算结果、配置数据缺少缓存层——
  1. 重复调用 LLM API -> 浪费 token 配额/费用
  2. 每个模块自己写 lru_cache / dict 缓存 -> 无 TTL、无驱逐策略、内存无限膨胀
  3. 没有 Cache 接口 -> 无法切换到 Redis / memcached

设计对标：
  - Spring Cache Abstraction（@Cacheable / CacheManager / 多后端）
  - Google Guava Cache（TTL + 最大容量 + LRU 驱逐）
  - Python functools.lru_cache（仅内存、无 TTL——不足以生产使用）

设计原则：
  - 统一 Cache 接口（get / set / delete / clear / stats）——后端可替换
  - TTL 支持——所有缓存条目必须有过期时间
  - 最大容量——防止内存膨胀
  - async-first

AI 施工约定：
  - LLM API 调用结果 MUST 缓存——用同样的 messages 调两次 = 浪费钱
  - 配置加载结果 SHOULD 缓存——YAML 不用反复读磁盘

SSoT: MOD-INF-016 §2.12 shared-cache
Version: 0.1.0
"""

from __future__ import annotations

from typing import Final
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "TTL_EXPIRED_DEFAULT_SECONDS",
    "CacheError",
    "CacheProvider",
    "CacheStats",
    "MemoryCache",
    "cache_key",
]

logger = logging.getLogger(__name__)

T = TypeVar("T")

TTL_EXPIRED_DEFAULT_SECONDS: Final[int] = 300


class CacheError(ZephyrBaseError):
    """缓存操作失败——后端不可达、key 冲突、序列化失败。"""
    error_code = "ZA-SH-0045"


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    errors: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total


class CacheProvider(Protocol):
    """缓存后端接口——获取/设置/删除/清空/统计。"""

    async def get(self, key: str) -> Any | None: ...
    async def set(self, key: str, value: Any, *, ttl_seconds: int = TTL_EXPIRED_DEFAULT_SECONDS) -> None: ...
    async def delete(self, key: str) -> bool: ...
    async def clear(self) -> None: ...
    def stats(self) -> CacheStats: ...


@dataclass
class _CacheEntry:
    value: Any
    expires_at: float


class MemoryCache:
    """内存缓存——TTL + LRU 驱逐 + 最大容量。

    对标 Python functools.lru_cache + Guava Cache 的生产增强。

    Usage::

        cache = MemoryCache(max_size=1000, default_ttl_seconds=600)
        await cache.set("llm:chat:abc123", response, ttl_seconds=3600)
        result = await cache.get("llm:chat:abc123")
        print(cache.stats())
    """

    def __init__(
        self,
        max_size: int = 1024,
        default_ttl_seconds: int = TTL_EXPIRED_DEFAULT_SECONDS,
    ) -> None:
        self._max_size = max_size
        self._default_ttl = default_ttl_seconds
        self._store: dict[str, _CacheEntry] = {}
        # 5.24.5 修复：list O(n) remove/pop(0) -> OrderedDict O(1) move_to_end/popitem
        self._access_order: OrderedDict[str, None] = OrderedDict()
        self._stats = CacheStats(max_size=max_size)

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired_keys = [k for k, entry in self._store.items() if entry.expires_at <= now]
        for k in expired_keys:
            del self._store[k]
            del self._access_order[k]  # O(1)
            self._stats.evictions += 1

    def _evict_lru(self) -> None:
        while len(self._store) >= self._max_size and self._access_order:
            oldest, _ = self._access_order.popitem(last=False)  # O(1) LRU 驱逐
            if oldest in self._store:
                del self._store[oldest]
                self._stats.evictions += 1

    def _touch(self, key: str) -> None:
        if key in self._access_order:
            self._access_order.move_to_end(key)  # O(1)
        else:
            self._access_order[key] = None  # O(1)

    async def get(self, key: str) -> Any | None:
        self._evict_expired()

        entry = self._store.get(key)
        if entry is None:
            self._stats.misses += 1
            return None

        self._stats.hits += 1
        self._touch(key)
        return entry.value

    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        effective_ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        expires_at = time.monotonic() + effective_ttl

        self._evict_expired()
        self._evict_lru()

        self._store[key] = _CacheEntry(value=value, expires_at=expires_at)
        self._touch(key)
        self._stats.size = len(self._store)

    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            if key in self._access_order:
                del self._access_order[key]  # O(1)
            self._stats.size = len(self._store)
            return True
        return False

    async def clear(self) -> None:
        self._store.clear()
        self._access_order.clear()
        self._stats.size = 0

    def stats(self) -> CacheStats:
        self._stats.size = len(self._store)
        return self._stats


def cache_key(*parts: str) -> str:
    """构造确定性缓存 key——用 ':' 分隔各段。

    Usage::

        key = cache_key("llm", "chat", model, str(hash(json.dumps(messages, sort_keys=True))))
    """
    return ":".join(parts)
