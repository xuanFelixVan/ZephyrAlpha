# [BLUEPRINT] MOD-SHARED-005 | docs/03_modules/_domain_shared/cache_consistency_manager/blueprint.md
# [MODULE] zephyr.shared.io.cache_consistency_manager
# [DOMAIN] D_SHARED
# [DEPENDENCIES] 无（协议核心纯内存；clock/alert_sink 全注入；cache_invalidation 语义参照不 import）
# [CONSUMERS] 运行时装配批（分层缓存注册 / 写策略裁定读侧 / 一致性巡检计划任务）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 键须先注册方可读写; 失效策略词表闭合(ttl|event|version)且 ttl 策略必带正 ttl_seconds; 写策略按数据类型注册(write_through|write_back)未注册 Fail-Closed; 版本戳单调递增(回退拒绝); write_back 脏条目 flush 前不落已提交视图; 巡检按 key 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_shared/cache_consistency_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CacheConsistencyError(占位 ZA-SH-UNREGISTERED-CACHE-CONSISTENCY)——空key/未知键/非法策略/版本回退/策略与操作错配/缺源版本戳时抛
# [TESTS] tests/shared/io/test_cache_consistency_manager.py
# [A_module] module_id=MOD-SHARED-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""CacheConsistencyManager — 缓存一致性管理器（MOD-SHARED-005）。

B13-04324（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-SHARED-003，A3数据架构）：
分层缓存注册（L1内存/L2 Redis/L3 磁盘语义）+ 失效策略（TTL/事件失效/版本
戳三策略注册表）+ 写穿写回策略裁定（按数据类型注册表）+ 一致性巡检（抽样
比对源版本戳，不一致清单 + 告警回调）。

查重分工（蓝图 §0）：cache_invalidation=事件驱动失效广播（本件=策略注册
与一致性裁定，消费其失效事件但不重建广播总线）；io_cache=读写缓存实现
（本件不实现缓存存储，只治理元数据与一致性状态机）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "CacheConsistencyError",
    "CacheConsistencyManager",
    "CacheEntrySnapshot",
    "CacheTier",
    "InconsistencyRecord",
    "InvalidationStrategy",
    "WritePolicy",
]


class CacheConsistencyError(Exception):
    """缓存一致性输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SH-UNREGISTERED-CACHE-CONSISTENCY。
    """


class CacheTier(str, Enum):
    """缓存层级（词表闭合）。"""

    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISK = "l3_disk"


class InvalidationStrategy(str, Enum):
    """失效策略（词表闭合）。"""

    TTL = "ttl"
    EVENT = "event"
    VERSION = "version"


class WritePolicy(str, Enum):
    """写策略（词表闭合）。"""

    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"


@dataclass(frozen=True)
class CacheEntrySnapshot:
    """缓存条目快照（观测用，frozen）。"""

    key: str
    value: object
    version: int
    dirty: bool
    written_at: datetime.datetime


@dataclass(frozen=True)
class InconsistencyRecord:
    """巡检不一致记录（告警载荷）。"""

    key: str
    cached_version: int
    source_version: int | None  # None = 源侧缺版本戳


@dataclass
class _Entry:
    """缓存条目内部状态。"""

    data_type: str
    tiers: tuple[CacheTier, ...]
    strategy: InvalidationStrategy
    ttl_seconds: float | None
    value: object = None
    version: int = -1
    dirty: bool = False
    event_invalidated: bool = False
    written_at: datetime.datetime | None = None


class CacheConsistencyManager:
    """缓存一致性管理器（分层注册 + 失效策略 + 写策略裁定 + 巡检）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[InconsistencyRecord], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._entries: dict[str, _Entry] = {}
        self._write_policies: dict[str, WritePolicy] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _entry_of(self, key: str) -> _Entry:
        entry = self._entries.get(key)
        if entry is None:
            raise CacheConsistencyError(f"未知缓存键: {key!r}（须先 register_entry）")
        return entry

    # ── 注册 ─────────────────────────────────────────────────────────────

    def register_entry(
        self,
        key: str,
        *,
        data_type: str,
        tiers: Iterable[CacheTier],
        strategy: InvalidationStrategy,
        ttl_seconds: float | None = None,
    ) -> None:
        """注册受治理缓存键（重复注册拒绝；TTL 策略强制正 ttl_seconds）。"""
        if not key:
            raise CacheConsistencyError("key 为空")
        if not data_type:
            raise CacheConsistencyError("data_type 为空")
        if not isinstance(strategy, InvalidationStrategy):
            raise CacheConsistencyError(f"非法失效策略: {strategy!r}")
        tier_tuple = tuple(tiers)
        if not tier_tuple:
            raise CacheConsistencyError("tiers 为空（至少登记一层）")
        for tier in tier_tuple:
            if not isinstance(tier, CacheTier):
                raise CacheConsistencyError(f"非法缓存层: {tier!r}")
        if strategy is InvalidationStrategy.TTL:
            if ttl_seconds is None or ttl_seconds <= 0:
                raise CacheConsistencyError("TTL 策略须配正 ttl_seconds")
        elif ttl_seconds is not None:
            raise CacheConsistencyError(f"{strategy.value} 策略不接受 ttl_seconds")
        if key in self._entries:
            raise CacheConsistencyError(f"缓存键重复注册: {key!r}")
        self._entries[key] = _Entry(
            data_type=data_type,
            tiers=tier_tuple,
            strategy=strategy,
            ttl_seconds=ttl_seconds,
        )

    def set_write_policy(self, data_type: str, policy: WritePolicy) -> None:
        """按数据类型注册写穿/写回策略（重复注册拒绝防裁定漂移）。"""
        if not data_type:
            raise CacheConsistencyError("data_type 为空")
        if not isinstance(policy, WritePolicy):
            raise CacheConsistencyError(f"非法写策略: {policy!r}")
        if data_type in self._write_policies:
            raise CacheConsistencyError(f"数据类型 {data_type!r} 写策略已注册")
        self._write_policies[data_type] = policy

    def write_policy_for(self, data_type: str) -> WritePolicy:
        """写策略裁定查询（未注册 Fail-Closed）。"""
        policy = self._write_policies.get(data_type)
        if policy is None:
            raise CacheConsistencyError(f"数据类型 {data_type!r} 未注册写策略")
        return policy

    # ── 写入 ─────────────────────────────────────────────────────────────

    def write(self, key: str, value: object, *, version: int) -> None:
        """写入：版本单调递增；按数据类型裁定写穿(立即提交)/写回(脏标记)。"""
        if version < 0:
            raise CacheConsistencyError(f"version 非法: {version!r}（须 ≥ 0）")
        entry = self._entry_of(key)
        policy = self.write_policy_for(entry.data_type)
        if entry.written_at is not None and version <= entry.version:
            raise CacheConsistencyError(
                f"版本回退拒绝: {key!r} 当前 v{entry.version}，写入 v{version}"
            )
        entry.value = value
        entry.version = version
        entry.written_at = self._clock()
        entry.event_invalidated = False  # 新写入复位事件失效标记
        entry.dirty = policy is WritePolicy.WRITE_BACK

    def flush(self, key: str) -> bool:
        """写回条目落盘提交（清脏标记）；本已干净 → 幂等返回 False。"""
        entry = self._entry_of(key)
        if not entry.dirty:
            return False
        entry.dirty = False
        return True

    # ── 失效与有效性 ──────────────────────────────────────────────────────

    def invalidate(self, key: str) -> None:
        """事件失效（仅 EVENT 策略条目可事件失效，其余策略错配拒绝）。"""
        entry = self._entry_of(key)
        if entry.strategy is not InvalidationStrategy.EVENT:
            raise CacheConsistencyError(
                f"键 {key!r} 策略为 {entry.strategy.value}，不接受事件失效"
            )
        entry.event_invalidated = True
        _log.info("缓存事件失效: %s", key)

    def is_valid(self, key: str, *, source_version: int | None = None) -> bool:
        """有效性裁定：TTL 比注入时钟；EVENT 看失效标记；VERSION 比源版本戳。"""
        entry = self._entry_of(key)
        if entry.written_at is None:
            return False  # 从未写入
        if entry.strategy is InvalidationStrategy.TTL:
            assert entry.ttl_seconds is not None  # 注册时已强制
            elapsed = (self._clock() - entry.written_at).total_seconds()
            return elapsed <= entry.ttl_seconds
        if entry.strategy is InvalidationStrategy.EVENT:
            return not entry.event_invalidated
        # VERSION
        if source_version is None:
            raise CacheConsistencyError(f"VERSION 策略键 {key!r} 有效性判定缺 source_version")
        return entry.version == source_version

    def read(self, key: str, *, source_version: int | None = None) -> object | None:
        """读：无效条目返回 None（未命中语义）。"""
        if not self.is_valid(key, source_version=source_version):
            return None
        return self._entry_of(key).value

    def snapshot(self, key: str) -> CacheEntrySnapshot:
        """条目快照（未写入 → Fail-Closed）。"""
        entry = self._entry_of(key)
        if entry.written_at is None:
            raise CacheConsistencyError(f"键 {key!r} 从未写入，无快照")
        return CacheEntrySnapshot(
            key=key,
            value=entry.value,
            version=entry.version,
            dirty=entry.dirty,
            written_at=entry.written_at,
        )

    # ── 一致性巡检 ────────────────────────────────────────────────────────

    def patrol(
        self,
        source_versions: Mapping[str, int],
        *,
        sample_keys: Iterable[str] | None = None,
    ) -> tuple[InconsistencyRecord, ...]:
        """一致性巡检：抽样比对源版本戳 → 不一致清单 + 逐条告警回调。

        sample_keys 缺省=全量注册键；输出按 key 确定性排序。
        """
        keys = sorted(sample_keys) if sample_keys is not None else sorted(self._entries)
        records: list[InconsistencyRecord] = []
        for key in keys:
            entry = self._entry_of(key)  # 抽样含未注册键 → Fail-Closed
            source_version = source_versions.get(key)
            if entry.written_at is None and source_version is None:
                continue  # 双侧皆空，视为一致（无数据）
            if entry.written_at is not None and source_version == entry.version:
                continue  # 版本戳一致
            cached = entry.version if entry.written_at is not None else -1
            records.append(InconsistencyRecord(
                key=key, cached_version=cached, source_version=source_version,
            ))
        for record in records:
            _log.warning(
                "缓存不一致: %s（缓存 v%d / 源 %s）",
                record.key, record.cached_version,
                f"v{record.source_version}" if record.source_version is not None else "缺版本戳",
            )
            if self._alert_sink is not None:
                self._alert_sink(record)
        return tuple(records)

    def keys(self) -> tuple[str, ...]:
        """已注册键清单（确定性排序）。"""
        return tuple(sorted(self._entries))
