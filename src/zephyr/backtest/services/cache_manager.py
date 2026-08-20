# [BLUEPRINT] MOD-BT-020 | docs/03_modules/_domain_backtest/cache_manager/blueprint.md
# [MODULE] zephyr.backtest.services.cache_manager
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-BT-021(param_analyzer) ; MOD-BT-024(result_comparator)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CacheKey/Config/Stats/Entry frozen不可变; LRU OrderedDict淘汰; 线程安全(Lock); get未命中返回None不报错
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CacheError(ZA-BT-0020)
# [TESTS] tests/backtest/test_cache_manager.py
# [A_module] module_id=MOD-BT-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_BACKTEST — Backtest Cache Manager (回测缓存管理器)

回测结果内存缓存与复用。基于策略ID+参数哈希+日期范围计算缓存键,
LRU淘汰策略管理容量, 支持按键/按策略/全量失效, 提供命中率统计。

属 A 类基础设施(纯内存管理+哈希计算), 纯基础层不涉及策略。

设计真源: depgraph MOD-BT-020
蓝图: docs/03_modules/_domain_backtest/cache_manager/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 缓存键要素 函数参数
#   fields: strategy_id + params dict + start_date + end_date + benchmark_symbol可选
#   code: compute_key L171-212
# - id: I2
#   name: 回测结果对象 object
#   fields: 任意待缓存的回测结果value
#   code: put L246-272
# - id: I3
#   name: 缓存配置 CacheConfig frozen
#   fields: max_entries=256 + max_size_bytes=0(0=不限)
#   code: CacheConfig L58-80
# 层: 算法
# - id: A1
#   name_zh: ① 缓存键哈希计算
#   name_en: compute_key
#   intro: 参数JSON序列化后SHA256取前16位当指纹，同参必同键
#   desc: strategy_id/日期非空校验 → json.dumps(sort_keys=True) → sha256.hexdigest()[:16] → 组装frozen CacheKey（L171-212）
#   inputs: I1
#   outputs: CacheKey
#   invariant: 相同strategy_id+params_hash+日期范围必得相同CacheKey
# - id: A2
#   name_zh: ② LRU读写与淘汰
#   name_en: get/put
#   intro: 命中移到队尾标记最近用，容量超限从队头弹最旧条目
#   desc: Lock内get命中move_to_end+hit_count+1未命中返回None → put插入移尾 → len>max_entries时popitem(last=False)淘汰（L217-272）
#   inputs: A1 I2 I3
#   outputs: 缓存值或None
#   invariant: 未命中返回None不报错; Lock线程安全; Entry frozen不可变
# - id: A3
#   name_zh: ③ 缓存失效管理
#   name_en: invalidate/invalidate_strategy/clear
#   intro: 按键/按策略/全量三种粒度删缓存
#   desc: invalidate删单键 → invalidate_strategy按strategy_id扫键批量删 → clear全量清空（L277-325）
#   inputs: A1
#   outputs: 删除条数
# - id: A4
#   name_zh: ④ 命中率统计快照
#   name_en: stats
#   intro: 汇总命中/未命中/淘汰计数出不可变快照
#   desc: Lock内读计数器组装CacheStats → hit_rate=hits/(hits+misses)（L330-342, L137-141）
#   inputs: A2
#   outputs: CacheStats
# 层: 输出
# - id: O1
#   name_zh: 缓存命中的回测结果 value或None
#   name_en: cached_value
#   intro: 命中直接复用回测结果，未命中返回None由调用方重算
#   invariant: 未命中返回None不报错
#   downstream: param_analyzer MOD-BT-021 ; result_comparator MOD-BT-024
# - id: O2
#   name_zh: 缓存统计快照 CacheStats
#   name_en: CacheStats
#   intro: 命中/未命中/淘汰/条目数+命中率，供调用方监控缓存效果
#   downstream: param_analyzer MOD-BT-021 ; result_comparator MOD-BT-024
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A2
# I3 --> A2
# A1 --> A3
# A2 --> A4
# A2 --> O1
# A4 --> O2
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "CacheError",
    "CacheConfig",
    "CacheKey",
    "CacheEntry",
    "CacheStats",
    "BacktestCacheManager",
]

_logger = logging.getLogger(__name__)


class CacheError(ZephyrBaseError):
    """缓存操作异常——配置非法或键计算失败。"""

    error_code = "ZA-BT-0020"


@dataclass(frozen=True)
class CacheConfig:
    """缓存配置——不可变。

    Attributes:
        max_entries: 最大缓存条目数 (LRU 淘汰)。
        max_size_bytes: 最大缓存大小(字节), 0=不限。
    """

    max_entries: int = 256
    max_size_bytes: int = 0

    def __post_init__(self) -> None:
        if self.max_entries <= 0:
            raise CacheError(
                f"max_entries must be > 0, got {self.max_entries}",
                details={"max_entries": self.max_entries},
            )
        if self.max_size_bytes < 0:
            raise CacheError(
                f"max_size_bytes must be >= 0, got {self.max_size_bytes}",
                details={"max_size_bytes": self.max_size_bytes},
            )


@dataclass(frozen=True)
class CacheKey:
    """缓存键——不可变。

    相同 strategy_id + params_hash + date range → 相同 CacheKey → 命中缓存。

    Attributes:
        strategy_id: 策略 ID。
        params_hash: 参数 SHA-256 哈希前 16 位。
        start_date: 回测开始日期 (ISO 字符串)。
        end_date: 回测结束日期 (ISO 字符串)。
        benchmark_symbol: 基准标的 (可选)。
    """

    strategy_id: str
    params_hash: str
    start_date: str
    end_date: str
    benchmark_symbol: str | None = None


@dataclass(frozen=True)
class CacheEntry:
    """缓存条目——不可变。

    Attributes:
        key: 缓存键。
        value: 缓存的回测结果。
        created_at: 创建时间 (ISO 字符串)。
        hit_count: 命中次数。
    """

    key: CacheKey
    value: Any
    created_at: str
    hit_count: int = 0


@dataclass(frozen=True)
class CacheStats:
    """缓存统计——不可变。

    Attributes:
        hits: 命中次数。
        misses: 未命中次数。
        evictions: LRU 淘汰次数。
        total_entries: 当前缓存条目数。
    """

    hits: int
    misses: int
    evictions: int
    total_entries: int

    @property
    def hit_rate(self) -> float:
        """命中率 = hits / (hits + misses)。"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class BacktestCacheManager:
    """回测缓存管理器——LRU 内存缓存 + 命中率统计。

    Usage:
        mgr = BacktestCacheManager()
        key = mgr.compute_key("strat_a", {"fast": 5, "slow": 20}, "2024-01-01", "2024-06-30")
        mgr.put(key, backtest_result)
        cached = mgr.get(key)  # 命中→返回结果, 未命中→None
        print(mgr.stats())
    """

    def __init__(self, config: CacheConfig | None = None) -> None:
        self._config = config if config is not None else CacheConfig()
        self._store: OrderedDict[CacheKey, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    @property
    def config(self) -> CacheConfig:
        """配置 (只读)。"""
        return self._config

    # ------------------------------------------------------------------
    # 缓存键计算
    # ------------------------------------------------------------------
    def compute_key(
        self,
        strategy_id: str,
        params: dict,
        start_date: str,
        end_date: str,
        benchmark_symbol: str | None = None,
    ) -> CacheKey:
        """根据回测参数计算缓存键。

        Args:
            strategy_id: 策略 ID。
            params: 策略参数字典 (会序列化为 JSON 并哈希)。
            start_date: 回测开始日期。
            end_date: 回测结束日期。
            benchmark_symbol: 基准标的 (可选)。

        Returns:
            CacheKey

        Raises:
            CacheError: strategy_id 为空 / 日期为空。
        """
        if not strategy_id:
            raise CacheError("strategy_id 不能为空")
        if not start_date or not end_date:
            raise CacheError("start_date 和 end_date 不能为空")
        try:
            params_str = json.dumps(params, sort_keys=True, default=str)
        except (TypeError, ValueError) as e:
            raise CacheError(
                f"params 序列化失败: {e}",
                details={"params_type": type(params).__name__},
            ) from e
        params_hash = hashlib.sha256(params_str.encode("utf-8")).hexdigest()[:16]
        return CacheKey(
            strategy_id=strategy_id,
            params_hash=params_hash,
            start_date=str(start_date),
            end_date=str(end_date),
            benchmark_symbol=benchmark_symbol,
        )

    # ------------------------------------------------------------------
    # 缓存读写
    # ------------------------------------------------------------------
    def get(self, key: CacheKey) -> object | None:
        """获取缓存值。命中返回值, 未命中返回 None。

        Args:
            key: 缓存键。

        Returns:
            缓存的值, 或 None (未命中)。
        """
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._misses += 1
                _logger.debug("缓存未命中: %s", key)
                return None
            # LRU: 移到末尾 (最近使用)
            self._store.move_to_end(key)
            self._hits += 1
            # 更新 hit_count (创建新 frozen entry)
            updated = CacheEntry(
                key=entry.key,
                value=entry.value,
                created_at=entry.created_at,
                hit_count=entry.hit_count + 1,
            )
            self._store[key] = updated
            _logger.debug("缓存命中: %s (hit_count=%d)", key, updated.hit_count)
            return entry.value

    def put(self, key: CacheKey, value: object) -> bool:
        """存入缓存。如果键已存在则覆盖。

        Args:
            key: 缓存键。
            value: 要缓存的值。

        Returns:
            True=新插入, False=覆盖已有条目。
        """
        with self._lock:
            is_new = key not in self._store
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=_now_iso(),
                hit_count=0,
            )
            self._store[key] = entry
            # LRU: 新插入的移到末尾
            self._store.move_to_end(key)
            # 淘汰超出容量的最旧条目
            while len(self._store) > self._config.max_entries:
                self._store.popitem(last=False)  # 弹出最旧的 (OrderedDict 头部)
                self._evictions += 1
                _logger.debug("LRU 淘汰, 当前条目数=%d", len(self._store))
            return is_new

    # ------------------------------------------------------------------
    # 失效
    # ------------------------------------------------------------------
    def invalidate(self, key: CacheKey) -> bool:
        """失效单个缓存键。

        Args:
            key: 要失效的缓存键。

        Returns:
            True=存在并删除, False=不存在。
        """
        with self._lock:
            if key in self._store:
                del self._store[key]
                _logger.debug("缓存失效: %s", key)
                return True
            return False

    def invalidate_strategy(self, strategy_id: str) -> int:
        """失效指定策略的所有缓存。

        Args:
            strategy_id: 策略 ID。

        Returns:
            删除的条目数。
        """
        if not strategy_id:
            return 0
        with self._lock:
            keys_to_remove = [k for k in self._store if k.strategy_id == strategy_id]
            for k in keys_to_remove:
                del self._store[k]
            _logger.debug("策略 %s 缓存失效: 删除 %d 条", strategy_id, len(keys_to_remove))
            return len(keys_to_remove)

    def clear(self) -> int:
        """清空全部缓存。

        Returns:
            清空前的条目数。
        """
        with self._lock:
            count = len(self._store)
            self._store.clear()
            _logger.debug("缓存全量清空: %d 条", count)
            return count

    # ------------------------------------------------------------------
    # 统计
    # ------------------------------------------------------------------
    def stats(self) -> CacheStats:
        """获取缓存统计快照。

        Returns:
            CacheStats (不可变快照)。
        """
        with self._lock:
            return CacheStats(
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
                total_entries=len(self._store),
            )


def _now_iso() -> str:
    """当前 UTC 时间 ISO 字符串 (无第三方依赖)。"""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
