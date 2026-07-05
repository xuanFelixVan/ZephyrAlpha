# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.cache_layer
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INT_cache_layer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU
==================================================
蓝图 §6 · §3 · embedding memoization + 查询缓存

策略
----
- rules (不变,高频读) → 永久缓存
- execution_traces (流式写入,低频读) → 不缓存
- 其他 Collection → LRU 缓存 (默认 1024 条)
"""

from __future__ import annotations

import hashlib
import logging
import threading
from typing import Any

import numpy as np

_logger = logging.getLogger(__name__)

DEFAULT_CACHE_SIZE: int = 1024

PERMANENT_CACHE_COLLECTIONS: frozenset[str] = frozenset({"rules"})
NO_CACHE_COLLECTIONS: frozenset[str] = frozenset({"execution_traces"})


class CacheLayer:
    def __init__(self, max_size: int = DEFAULT_CACHE_SIZE) -> None:
        self._max_size = max_size
        self._embedding_cache: dict[str, np.ndarray] = {}
        self._query_cache: dict[str, list[dict[str, Any]]] = {}
        self._access_order: list[str] = []
        self._lock = threading.Lock()

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]

    @staticmethod
    def _cache_key(text_hash: str, model_version: str = "", collection: str = "") -> str:
        parts = []
        if collection:
            parts.append(collection)
        parts.append(text_hash)
        base = ":".join(parts)
        return f"{base}::{model_version}" if model_version else base

    def get_embedding(self, text: str, model_version: str = "", collection: str = "") -> np.ndarray | None:
        key = self._cache_key(self._hash_text(text), model_version, collection)
        with self._lock:
            # 5.85.1 修复：原 get 返回 self._embedding_cache[key]（直接引用），put 存储 vec.copy()。读写不对称。
            # 调用方拿到 get 返回的对象后修改它，直接篡改了cache内部状态。
            val = self._embedding_cache.get(key)
            return val.copy() if val is not None else None

    def put_embedding(self, text: str, vec: np.ndarray, model_version: str = "", collection: str = "") -> None:
        key = self._cache_key(self._hash_text(text), model_version, collection)
        with self._lock:
            if len(self._embedding_cache) >= self._max_size:
                self._evict_lru()
            self._embedding_cache[key] = vec.copy()
            self._access_order.append(key)

    def get_query_result(self, query: str, collection: str) -> list[dict[str, Any]] | None:
        key = self._cache_key(self._hash_text(query), collection=collection)
        with self._lock:
            return self._query_cache.get(key)

    def put_query_result(self, query: str, collection: str, results: list[dict[str, Any]]) -> None:
        key = self._cache_key(self._hash_text(query), collection=collection)
        with self._lock:
            if len(self._query_cache) >= self._max_size:
                self._evict_lru()
            self._query_cache[key] = results
            self._access_order.append(key)

    def should_cache_embedding(self, collection_name: str) -> bool:
        if collection_name in NO_CACHE_COLLECTIONS:
            return False
        return True

    def should_cache_query(self, collection_name: str) -> bool:
        if collection_name in NO_CACHE_COLLECTIONS:
            return False
        return True

    def invalidate_collection(self, collection_name: str) -> None:
        _logger.info("CacheLayer: 清除 Collection '%s' 缓存", collection_name)
        prefix = f"{collection_name}:"
        with self._lock:
            keys_to_remove = [k for k in self._embedding_cache if k.startswith(prefix)]
            for k in keys_to_remove:
                self._embedding_cache.pop(k, None)
            keys_to_remove_q = [k for k in self._query_cache if k.startswith(prefix)]
            for k in keys_to_remove_q:
                self._query_cache.pop(k, None)
            self._access_order = [k for k in self._access_order if k not in set(keys_to_remove) | set(keys_to_remove_q)]

    def invalidate_all(self) -> None:
        _logger.info("CacheLayer: 清除全部缓存")
        self._clear_all()

    def invalidate_all_on_model_change(self, new_model_version: str, old_model_version: str = "") -> None:
        _logger.info(
            "CacheLayer: 模型版本变更 %s → %s，清除全部缓存 (mitigates R7)", old_model_version, new_model_version
        )
        self._clear_all()

    def _clear_all(self) -> None:
        with self._lock:
            self._embedding_cache.clear()
            self._query_cache.clear()
            self._access_order.clear()

    def _evict_lru(self) -> None:
        if self._access_order:
            oldest = self._access_order.pop(0)
            self._embedding_cache.pop(oldest, None)
            self._query_cache.pop(oldest, None)

    @property
    def embedding_cache_size(self) -> int:
        return len(self._embedding_cache)

    @property
    def query_cache_size(self) -> int:
        return len(self._query_cache)
