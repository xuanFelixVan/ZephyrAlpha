# [BLUEPRINT] MOD-INF-042 | docs/03_modules/_domain_integration/blueprint.md | §3.1
# [MODULE] zephyr.integration.local_model.cache_layer
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-042 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""


CacheLayer — MOD-INF-011 嵌入缓存与查询结果 LRU
==================================================
蓝图 §6 · §3 · embedding memoization + 查询缓存

策略
----
- rules (不变,高频读) -> 永久缓存
- execution_traces (流式写入,低频读) -> 不缓存
- 其他 Collection -> LRU 缓存 (默认 1024 条)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 文本与查询串
#   fields: text 待嵌入文本 / query 查询串（字符串）
#   code: get_embedding(text) / get_query_result(query) L80/L96
# - id: I2
#   name: 嵌入向量与查询结果
#   fields: vec np.ndarray 嵌入向量 / results list[dict] 查询结果
#   code: put_embedding(text, vec) / put_query_result L88/L101
# - id: I3
#   name: 缓存维度参数
#   fields: collection 集合名 / model_version 模型版本 / max_size 容量（默认 1024）
#   code: CacheLayer.__init__(max_size) L50
# 层: 算法
# - id: A1
#   name_zh: ① 缓存键生成
#   name_en: _hash_text / _cache_key
#   intro: 把文本哈希成短指纹，再拼上集合名和模型版本做缓存键
#   desc: sha256(text).hexdigest()[:32]；key="collection:hash" 或 "collection:hash::model_version"
#   inputs: I1 I3
#   outputs: 缓存键字符串
# - id: A2
#   name_zh: ② 嵌入缓存读写
#   name_en: get_embedding / put_embedding
#   intro: 嵌入向量按键存取，进出都拷一份防止外部改坏缓存
#   desc: get 返回 val.copy()、put 存 vec.copy()（读写对称防篡改，5.85.1 修复）；写入前满 max_size 先 _evict_lru
#   inputs: I2 A1
#   outputs: np.ndarray 副本或 None
# - id: A3
#   name_zh: ③ 查询结果缓存读写
#   name_en: get_query_result / put_query_result
#   intro: 查询结果列表按键存取，同样满了先淘汰最旧的
#   desc: 键只含 collection:hash（不带模型版本）；命中返回 list[dict]，未命中 None
#   inputs: I2 A1
#   outputs: 查询结果或 None
# - id: A4
#   name_zh: ④ LRU 淘汰
#   name_en: _evict_lru
#   intro: 缓存满了就把最早访问的键从嵌入表和查询表一起踢掉
#   desc: _access_order.pop(0) 取最旧 key；两 cache dict 同步 pop
#   inputs: A2 A3
#   outputs: 淘汰一个键位
#   invariant: 缓存规模 ≤ max_size
# - id: A5
#   name_zh: ⑤ 缓存策略判定
#   name_en: should_cache_embedding / should_cache_query
#   intro: execution_traces 这类流式写入的集合不缓存，其余都缓存
#   desc: collection ∈ NO_CACHE_COLLECTIONS(execution_traces) → False；否则 True
#   inputs: I3
#   outputs: True/False
# - id: A6
#   name_zh: ⑥ 缓存失效清除
#   name_en: invalidate_collection / invalidate_all_on_model_change
#   intro: 按集合前缀清缓存，模型版本一变就全部清空防旧向量污染
#   desc: invalidate_collection 删所有 "collection:" 前缀键并同步清 access_order；模型变更时 _clear_all 全清（mitigates R7）
#   inputs: I3
#   outputs: 缓存清空
# 层: 输出
# - id: O1
#   name_zh: 缓存命中结果
#   name_en: np.ndarray / list[dict] / None
#   intro: 命中返回嵌入向量副本或查询结果，未命中 None 让调用方回源计算
#   downstream: 本地模型检索内部使用（MOD-INF-011 体系，[CONSUMERS] 头未登记）
# - id: O2
#   name_zh: 缓存规模指标
#   name_en: embedding_cache_size / query_cache_size
#   intro: 两个缓存表当前条目数，供容量监控
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I2 --> A2
# A1 --> A2
# I2 --> A3
# A1 --> A3
# A2 --> A4
# A3 --> A4
# I3 --> A5
# I3 --> A6
# A4 --> A2
# A5 --> A2
# A6 --> A2
# A2 --> O1
# A3 --> O1
# A2 --> O2
"""

from __future__ import annotations

import hashlib
import logging
import threading
from typing import Any, Final

import numpy as np

_logger = logging.getLogger(__name__)

DEFAULT_CACHE_SIZE: Final[int] = 1024

PERMANENT_CACHE_COLLECTIONS: Final[frozenset[str]] = frozenset({"rules"})
NO_CACHE_COLLECTIONS: Final[frozenset[str]] = frozenset({"execution_traces"})


class CacheLayer:
    def __init__(self, max_size: int = DEFAULT_CACHE_SIZE) -> None:
        self._max_size = max_size
        self._embedding_cache: dict[str, np.ndarray] = {}
        self._query_cache: dict[str, list[dict[str, Any]]] = {}
        self._access_order: list[str] = []
        self._lock = threading.Lock()

    @staticmethod
    def hash_text(text: str) -> str:
        """Stage 4 公共化。"""
        return CacheLayer._hash_text(text)

    @staticmethod
    def _hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]

    @staticmethod
    def cache_key(text_hash: str, model_version: str = "", collection: str = "") -> str:
        """Stage 4 公共化。"""
        return CacheLayer._cache_key(text_hash, model_version, collection)

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
            "CacheLayer: 模型版本变更 %s -> %s，清除全部缓存 (mitigates R7)", old_model_version, new_model_version
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
