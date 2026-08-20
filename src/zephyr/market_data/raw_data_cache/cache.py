# [BLUEPRINT] MOD-MKT-006 | docs/03_modules/_domain_mkt_data/raw_data_cache/blueprint.md
# [MODULE] zephyr.market_data.raw_data_cache.cache
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.market_data.normalized_market_data_producer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CacheEntry/CacheConfig/CacheKey/CacheStats frozen不可变; 读写加threading.Lock; LRU+TTL双重淘汰; content_hash写入时计算
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CacheError(ZA-MKT-0006)
# [TESTS] tests/market_data/raw_data_cache/test_raw_data_cache.py
# [A_module] module_id=MOD-MKT-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_MKT_DATA — Raw Data Cache 实现 (原始数据缓存)

LRU + TTL 双重淘汰的内存缓存, 存储行情标准化前的原始数据。
线程安全, 含内容哈希校验。

属 A 类基础设施(内存缓存), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-006
蓝图: docs/03_modules/_domain_mkt_data/raw_data_cache/blueprint.md
"""

from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import Lock

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class CacheError(ZephyrBaseError):
    """缓存操作异常——空 symbol / 非法日期 / 非法 payload。"""

    error_code = "ZA-MKT-0006"


class EvictionPolicy(str, Enum):
    """淘汰策略。"""

    LRU = "lru"  # 仅容量淘汰
    TTL = "ttl"  # 仅时间淘汰
    LRU_TTL = "lru_ttl"  # 双重淘汰(默认)


@dataclass(frozen=True)
class CacheKey:
    """缓存键——symbol + date, 不可变。

    Attributes:
        symbol: 标的代码(标准化格式, 如 "600000.SH")
        date: 日期(YYYY-MM-DD)
    """

    symbol: str
    date: str

    def __post_init__(self) -> None:
        if not self.symbol:
            raise CacheError("symbol 不能为空")
        if not self.date:
            raise CacheError("date 不能为空")


@dataclass(frozen=True)
class CacheEntry:
    """缓存条目——不可变。

    Attributes:
        key: 缓存键(symbol + date)
        source_vendor: 数据来源 vendor_id
        raw_payload: 原始数据(字节)
        content_hash: 内容哈希(SHA-256 前16字符)
        fetched_at: 写入时间(UTC)
        payload_size: payload 字节数
        expires_at: 过期时间(UTC), None=不过期
    """

    key: CacheKey
    source_vendor: str
    raw_payload: bytes
    content_hash: str
    fetched_at: datetime
    payload_size: int
    expires_at: datetime | None

    @property
    def is_expired(self) -> bool:
        """是否已过期(TTL)。"""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at


@dataclass(frozen=True)
class CacheConfig:
    """缓存配置——不可变。

    Attributes:
        max_size: 最大条目数(达上限按 LRU 淘汰)
        ttl_seconds: TTL(秒), None=不过期
        policy: 淘汰策略
    """

    max_size: int = 10000
    ttl_seconds: int | None = 86400
    policy: EvictionPolicy = EvictionPolicy.LRU_TTL


@dataclass(frozen=True)
class CacheStats:
    """缓存统计——不可变快照。

    Attributes:
        total_entries: 当前条目数
        total_size_bytes: 当前总字节数
        hit_count: 命中次数
        miss_count: 未命中次数
        eviction_count: 淘汰次数
    """

    total_entries: int
    total_size_bytes: int
    hit_count: int
    miss_count: int
    eviction_count: int

    @property
    def hit_rate(self) -> float:
        """命中率(0.0~1.0)。"""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total


def _compute_hash(raw_payload: bytes) -> str:
    """计算 SHA-256 内容哈希(前16字符)。"""
    return hashlib.sha256(raw_payload).hexdigest()[:16]


def _make_expires_at(fetched_at: datetime, ttl_seconds: int | None) -> datetime | None:
    """根据 TTL 计算过期时间。"""
    if ttl_seconds is None:
        return None
    return fetched_at + timedelta(seconds=ttl_seconds)


class RawDataCache:
    """原始数据缓存——LRU + TTL 双重淘汰的内存缓存。

    存储行情标准化前的原始数据, 支持重放/恢复/审计。

    线程安全: 所有读写操作加 threading.Lock 保护。
    淘汰策略: LRU(容量超限) + TTL(时间过期) 双重淘汰。

    Usage:
        cache = RawDataCache(CacheConfig(max_size=1000, ttl_seconds=3600))

        # 写入
        entry = cache.put("600000.SH", "2026-08-01", b"raw bytes",
                          source_vendor="tushare")

        # 读取
        entry = cache.get("600000.SH", "2026-08-01")  # CacheEntry | None

        # 范围查询
        entries = cache.query("600000.SH", "2026-08-01", "2026-08-05")
    """

    def __init__(self, config: CacheConfig | None = None) -> None:
        self._config = config if config is not None else CacheConfig()
        # OrderedDict 实现 LRU: 末尾=最近访问, 首部=最久未访问
        self._store: OrderedDict[CacheKey, CacheEntry] = OrderedDict()
        self._lock = Lock()
        self._hit_count = 0
        self._miss_count = 0
        self._eviction_count = 0
        self._total_size = 0

    def put(
        self,
        symbol: str,
        date: str,
        raw_payload: bytes,
        source_vendor: str,
        ttl_seconds: int | None = None,
    ) -> CacheEntry:
        """写入缓存条目。

        - symbol/date 非空校验, 否则 raise CacheError
        - raw_payload 为空 bytes 允许(可能是合法的空数据), 但 source_vendor 不能为空
        - 同 key 覆盖更新(旧条目移出, 调整 _total_size)
        - 容量超限时按 LRU 淘汰最久未访问的条目
        - ttl_seconds 覆盖 config.ttl_seconds(默认 None=用 config)

        Args:
            symbol: 标的代码
            date: 日期(YYYY-MM-DD)
            raw_payload: 原始数据(字节)
            source_vendor: 数据来源 vendor_id
            ttl_seconds: 可选 TTL 覆盖

        Returns:
            写入的 CacheEntry

        Raises:
            CacheError: symbol/date/source_vendor 为空
        """
        if not symbol:
            raise CacheError("symbol 不能为空")
        if not date:
            raise CacheError("date 不能为空")
        if not source_vendor:
            raise CacheError("source_vendor 不能为空")
        if not isinstance(raw_payload, (bytes, bytearray)):
            raise CacheError(
                "raw_payload 必须是 bytes/bytearray",
                details={"type": type(raw_payload).__name__},
            )

        key = CacheKey(symbol=symbol, date=date)
        now = datetime.now(timezone.utc)
        effective_ttl = ttl_seconds if ttl_seconds is not None else self._config.ttl_seconds
        payload = bytes(raw_payload)
        entry = CacheEntry(
            key=key,
            source_vendor=source_vendor,
            raw_payload=payload,
            content_hash=_compute_hash(payload),
            fetched_at=now,
            payload_size=len(payload),
            expires_at=_make_expires_at(now, effective_ttl),
        )

        with self._lock:
            # 覆盖: 若 key 已存在, 先移除旧的
            if key in self._store:
                old = self._store.pop(key)
                self._total_size -= old.payload_size

            # 写入(末尾=最近)
            self._store[key] = entry
            self._total_size += entry.payload_size

            # LRU 淘汰: 容量超限时淘汰最久未访问(首部)
            self._evict_lru_locked()

        _logger.debug(
            "缓存写入: %s %s size=%d hash=%s",
            symbol,
            date,
            entry.payload_size,
            entry.content_hash,
        )
        return entry

    def get(self, symbol: str, date: str) -> CacheEntry | None:
        """读取缓存条目。

        - 命中且未过期: 移到末尾(标记最近访问), hit_count+1, 返回 entry
        - 命中但已过期: 移除(惰性淘汰), miss_count+1, 返回 None
        - 未命中: miss_count+1, 返回 None

        Returns:
            CacheEntry | None
        """
        key = CacheKey(symbol=symbol, date=date)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self._miss_count += 1
                return None

            # TTL 检查(惰性淘汰)
            if entry.is_expired:
                self._remove_locked(key)
                self._miss_count += 1
                _logger.debug("缓存命中但已过期: %s %s", symbol, date)
                return None

            # 命中: 移到末尾(LRU 更新)
            self._store.move_to_end(key)
            self._hit_count += 1
            return entry

    def query(self, symbol: str, start_date: str, end_date: str) -> list[CacheEntry]:
        """范围查询——返回 [start_date, end_date] 区间内该 symbol 的有效缓存条目。

        - 按日期升序返回
        - 跳过过期条目(惰性淘汰)
        - 不更新 LRU 顺序(只读查询)

        Args:
            symbol: 标的代码
            start_date: 起始日期(含, YYYY-MM-DD)
            end_date: 结束日期(含, YYYY-MM-DD)

        Returns:
            list[CacheEntry]: 有效缓存条目(日期升序)
        """
        results: list[CacheEntry] = []
        with self._lock:
            for key, entry in self._store.items():
                if key.symbol != symbol:
                    continue
                if start_date <= key.date <= end_date:
                    if not entry.is_expired:
                        results.append(entry)
        results.sort(key=lambda e: e.key.date)
        return results

    def exists(self, symbol: str, date: str) -> bool:
        """是否存在有效缓存条目(未过期)。不更新 LRU 顺序。"""
        key = CacheKey(symbol=symbol, date=date)
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return False
            if entry.is_expired:
                self._remove_locked(key)
                return False
            return True

    def evict_expired(self) -> int:
        """主动淘汰所有过期条目。

        Returns:
            淘汰的条目数
        """
        evicted = 0
        with self._lock:
            expired_keys = [k for k, e in self._store.items() if e.is_expired]
            for key in expired_keys:
                self._remove_locked(key)
                evicted += 1
        if evicted:
            _logger.info("主动淘汰过期缓存: %d 条", evicted)
        return evicted

    def clear(self) -> int:
        """清空所有缓存。

        Returns:
            清空的条目数
        """
        with self._lock:
            count = len(self._store)
            self._store.clear()
            self._total_size = 0
        if count:
            _logger.info("缓存清空: %d 条", count)
        return count

    @property
    def stats(self) -> CacheStats:
        """缓存统计快照(只读)。"""
        with self._lock:
            return CacheStats(
                total_entries=len(self._store),
                total_size_bytes=self._total_size,
                hit_count=self._hit_count,
                miss_count=self._miss_count,
                eviction_count=self._eviction_count,
            )

    @property
    def config(self) -> CacheConfig:
        """缓存配置(只读)。"""
        return self._config

    # ---- 内部方法(调用方已持有 _lock) ----

    def _remove_locked(self, key: CacheKey) -> None:
        """移除条目(调用方已持锁)。"""
        entry = self._store.pop(key, None)
        if entry is not None:
            self._total_size -= entry.payload_size

    def _evict_lru_locked(self) -> None:
        """LRU 淘汰: 容量超限时淘汰最久未访问(首部)。调用方已持锁。"""
        if self._config.policy == EvictionPolicy.TTL:
            return  # 仅 TTL 策略不做容量淘汰
        while len(self._store) > self._config.max_size:
            key, entry = self._store.popitem(last=False)
            self._total_size -= entry.payload_size
            self._eviction_count += 1
            _logger.debug("LRU 淘汰: %s %s (容量超限)", key.symbol, key.date)

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"RawDataCache(entries={len(self._store)}, "
                f"size={self._total_size}B, "
                f"max={self._config.max_size}, hits={self._hit_count}, "
                f"misses={self._miss_count})"
            )


__all__ = [
    "CacheConfig",
    "CacheEntry",
    "CacheError",
    "CacheKey",
    "CacheStats",
    "EvictionPolicy",
    "RawDataCache",
]
