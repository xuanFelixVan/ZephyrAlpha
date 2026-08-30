# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.storage_tiering
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.ch_reader; zephyr.data.tick_redis_cache
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 层级单调迁移(热→温→冷，禁跨层回迁); 分区粒度日线按年/分钟按月; UFL事实层追加式禁改; 复用现有CH/Redis/backup不重建
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非确定性事实写入/改删UFL→UFLMutationError; 未知分区频率/恢复级别→ValueError
# [TESTS] tests/zephyr/data/test_storage_tiering.py
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
冷热分层 TTL 自动迁移 + 分区 + UFL 事实层 + 双副本校验 + 恢复演练（CAND-DAT-006 / B1-00584）。

min_build_spec 对齐（深挖裁定=做 P0，复用现有 CH/Redis/backup 不重建）：
  1. 冷热分层 TTL 自动迁移：热 Redis（tick/bar 热键）→ 温 ClickHouse → 冷 Parquet 归档
  2. 分区策略：日线按年（year=YYYY）、分钟按月（year=YYYY/month=MM）
  3. UFL 追加式事实层：is_deterministic=True 方可写入，改/删一律 UFLMutationError
  4. D/E 双副本一致性校验：相对路径集合 + sha256 逐文件比对
  5. RTO/RPO 分级恢复演练：L1(<5min/≤1s) ~ L6(<240min/≤24h) 达标判定

后端全部注入式（redis_client / warm_insert / parquet_write / warm_drop），
本模块只承载迁移决策与校验逻辑闭环；真实 IO 由调用方接 ch_writer/ch_reader/
tick_redis_cache 现有能力，不重建存储栈。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: freq 参数
#   fields: 参数 freq，类型注解 str
#   code: storage_tiering.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: day 参数
#   fields: 参数 day，类型注解 date
#   code: storage_tiering.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: primary_root 参数
#   fields: 参数 primary_root，类型注解 Path
#   code: storage_tiering.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: replica_root 参数
#   fields: 参数 replica_root，类型注解 Path
#   code: storage_tiering.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① partition_key
#   name_en: partition_key
#   intro: 返回 Hive 风格分区键：日线 year=YYYY，分钟 year=YYYY/month=MM。
#   desc: 返回 Hive 风格分区键：日线 year=YYYY，分钟 year=YYYY/month=MM。 Raises: ValueError: 未知频率（仅支持 daily/minu…；源码 L155-L165
#   inputs: freq day
#   outputs: str
# - id: A2
#   name_zh: ② StorageTiering
#   name_en: StorageTiering
#   intro: 冷热分层 TTL 自动迁移管理器（决策逻辑闭环，IO 后端注入）。
#   desc: 冷热分层 TTL 自动迁移管理器（决策逻辑闭环，IO 后端注入）。 Usage: st = StorageTiering(TierPolicy(hot_ttl_seconds=3…；公共方法（定义序）: classif…
#   inputs: policy
#   outputs: 返回值
# - id: A3
#   name_zh: ③ UFLFactLayer
#   name_en: UFLFactLayer
#   intro: 追加式事实层：只增不改，重复同值幂等，异值/改/删一律拒绝。
#   desc: 追加式事实层：只增不改，重复同值幂等，异值/改/删一律拒绝。；公共方法（定义序）: count, append, get, update, delete；源码 L334-L363
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ ReplicaConsistencyReport
#   name_en: ReplicaConsistencyReport
#   intro: 双副本一致性报告。
#   desc: 双副本一致性报告。；公共方法（定义序）: consistent；源码 L372-L381
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ check_replica_consistency
#   name_en: check_replica_consistency
#   intro: 比对主副本（D盘）与副副本（E盘）：文件集合 + sha256 逐一核对。
#   desc: 比对主副本（D盘）与副副本（E盘）：文件集合 + sha256 逐一核对。；源码 L396-L407
#   inputs: primary_root replica_root
#   outputs: ReplicaConsistencyReport
# - id: A6
#   name_zh: ⑥ main
#   name_en: main
#   intro: 入口——待实现。
#   desc: 入口——待实现。；源码 L445-L446
#   inputs: 无参数
#   outputs: 返回值
#   （注：A6 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler
# - id: O2
#   name_zh: ReplicaConsistencyReport
#   name_en: ReplicaConsistencyReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

log = logging.getLogger(__name__)

__all__ = [
    "RECOVERY_LEVELS",
    "DrillResult",
    "MigrationReport",
    "ReplicaConsistencyReport",
    "StorageTiering",
    "Tier",
    "TierPolicy",
    "UFLFact",
    "UFLFactLayer",
    "UFLMutationError",
    "check_replica_consistency",
    "partition_key",
]


# ---------------------------------------------------------------------------
# 1. 分区策略（日线按年 / 分钟按月）
# ---------------------------------------------------------------------------

_FREQ_DAILY = "daily"
_FREQ_MINUTE = "minute"


def partition_key(freq: str, day: date) -> str:
    """返回 Hive 风格分区键：日线 year=YYYY，分钟 year=YYYY/month=MM。

    Raises:
        ValueError: 未知频率（仅支持 daily/minute）
    """
    if freq == _FREQ_DAILY:
        return f"year={day:%Y}"
    if freq == _FREQ_MINUTE:
        return f"year={day:%Y}/month={day:%m}"
    raise ValueError(f"未知分区频率: {freq!r}（仅支持 daily/minute）")


# ---------------------------------------------------------------------------
# 2. 层级与策略
# ---------------------------------------------------------------------------


class Tier(str, Enum):
    """存储层级（单调迁移方向 HOT→WARM→COLD）。"""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


@dataclass(frozen=True)
class TierPolicy:
    """分层策略。

    hot_ttl_seconds: 热层 TTL（秒），超过则迁往温层（CH）。
    warm_retention_days: 温层保留天数，超过则归档冷层（Parquet）。
    """

    hot_ttl_seconds: int = 300
    warm_retention_days: int = 365


class _HotBackend(Protocol):
    """热层后端协议（tick_redis_cache 的 redis.Client 子集）。"""

    def keys(self) -> Iterable[str]: ...

    def get(self, key: str) -> Any: ...

    def delete(self, key: str) -> Any: ...


@dataclass(frozen=True)
class MigrationReport:
    """一次迁移的结果计数。migrated=迁移条数，skipped=跳过条数。"""

    migrated: int = 0
    skipped: int = 0
    details: tuple[str, ...] = field(default_factory=tuple)


class StorageTiering:
    """冷热分层 TTL 自动迁移管理器（决策逻辑闭环，IO 后端注入）。

    Usage:
        st = StorageTiering(TierPolicy(hot_ttl_seconds=300, warm_retention_days=365))
        st.migrate_hot_to_warm(redis_client, warm_insert=ch_insert_fn)
        st.migrate_warm_to_cold("kline_daily", "daily", day, rows, parquet_write_fn, ch_drop_fn)
    """

    def __init__(self, policy: TierPolicy | None = None) -> None:
        self.policy = policy if policy is not None else TierPolicy()

    # ── 层级判定 ──
    def classify(self, ts: datetime, now: datetime) -> Tier:
        """按数据时间戳与当前时点的年龄判定目标层级。"""
        age = now - ts
        if age <= timedelta(seconds=self.policy.hot_ttl_seconds):
            return Tier.HOT
        if age <= timedelta(days=self.policy.warm_retention_days):
            return Tier.WARM
        return Tier.COLD

    # ── 热→温：Redis 热键过期迁移到 CH 温层 ──
    def migrate_hot_to_warm(
        self,
        redis_client: _HotBackend,
        warm_insert: Callable[[str, datetime, Any], None],
        now: datetime,
    ) -> MigrationReport:
        """扫描热层键，超过 hot_ttl 的写入温层后从热层删除。

        热层 value 约定为 (ts, payload) 二元组（tick_redis_cache 写入侧语义）。
        """
        migrated = 0
        skipped = 0
        moved_keys: list[str] = []
        for key in list(redis_client.keys()):
            entry = redis_client.get(key)
            if entry is None:
                skipped += 1
                continue
            ts, value = entry
            if self.classify(ts, now) is Tier.HOT:
                skipped += 1
                continue
            warm_insert(key, ts, value)
            redis_client.delete(key)
            migrated += 1
            moved_keys.append(key)
        if migrated:
            log.info("hot→warm 迁移 %d 键（跳过 %d）", migrated, skipped)
        return MigrationReport(migrated=migrated, skipped=skipped, details=tuple(moved_keys))

    # ── 温→冷：超保留期分区归档 Parquet ──
    def migrate_warm_to_cold(
        self,
        dataset: str,
        freq: str,
        partition_date: date,
        rows: list[Any],
        parquet_write: Callable[[str, list[Any]], None],
        warm_drop: Callable[[str, str], None],
        now: datetime,
    ) -> MigrationReport:
        """温层分区超过 warm_retention_days → 写 Parquet 冷层后删除温层分区。"""
        pkey = partition_key(freq, partition_date)
        partition_ts = datetime(partition_date.year, partition_date.month, partition_date.day, tzinfo=now.tzinfo)
        if self.classify(partition_ts, now) is not Tier.COLD:
            return MigrationReport(migrated=0, skipped=1)
        cold_path = f"{dataset}/{pkey}"
        parquet_write(cold_path, rows)
        warm_drop(dataset, pkey)
        log.info("warm→cold 归档 %s → %s（%d 行）", dataset, cold_path, len(rows))
        return MigrationReport(migrated=1, skipped=0, details=(cold_path,))

    # ── RTO/RPO 分级恢复演练 ──
    def evaluate_drill(
        self,
        level: str,
        observed_rto_minutes: float,
        observed_rpo_seconds: float,
    ) -> DrillResult:
        """按级别目标判定一次恢复演练是否达标。

        Raises:
            ValueError: 未知恢复级别
        """
        if level not in RECOVERY_LEVELS:
            raise ValueError(f"未知恢复级别: {level!r}（合法: {sorted(RECOVERY_LEVELS)}）")
        target = RECOVERY_LEVELS[level]
        passed = observed_rto_minutes <= target.rto_minutes and observed_rpo_seconds <= target.rpo_seconds
        return DrillResult(
            level=level,
            passed=passed,
            observed_rto_minutes=observed_rto_minutes,
            observed_rpo_seconds=observed_rpo_seconds,
            target=target,
        )


# ---------------------------------------------------------------------------
# 3. UFL 追加式事实层（is_deterministic=True 禁改校验）
# ---------------------------------------------------------------------------


class UFLMutationError(Exception):
    """UFL 事实层违规：非确定性写入或对既有事实的改/删。"""


@dataclass(frozen=True)
class UFLFact:
    """不可变事实记录（Universal Fact Layer）。

    is_deterministic: 必须 True——确定性重放可复现的事实才允许入层。
    """

    key: str
    value: Any
    ts: datetime
    is_deterministic: bool = True


class UFLFactLayer:
    """追加式事实层：只增不改，重复同值幂等，异值/改/删一律拒绝。"""

    def __init__(self) -> None:
        self._facts: dict[str, UFLFact] = {}

    @property
    def count(self) -> int:
        return len(self._facts)

    def append(self, fact: UFLFact) -> None:
        """追加事实。同 key 同 value 幂等放行；异值视为篡改，拒绝。"""
        if not fact.is_deterministic:
            raise UFLMutationError(f"UFL 拒收非确定性事实: {fact.key}（is_deterministic=False）")
        existing = self._facts.get(fact.key)
        if existing is not None:
            if existing.value == fact.value:
                return  # 幂等重放
            raise UFLMutationError(f"UFL 事实不可改: {fact.key} 已存在异值（追加式事实层禁改校验）")
        self._facts[fact.key] = fact

    def get(self, key: str) -> Any:
        fact = self._facts.get(key)
        return fact.value if fact is not None else None

    def update(self, key: str, value: Any) -> None:
        raise UFLMutationError(f"UFL 追加式事实层禁止 update: {key}")

    def delete(self, key: str) -> None:
        raise UFLMutationError(f"UFL 追加式事实层禁止 delete: {key}")


# ---------------------------------------------------------------------------
# 4. D/E 双副本一致性校验
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReplicaConsistencyReport:
    """双副本一致性报告。"""

    matched: int
    missing_in_replica: tuple[str, ...]
    hash_mismatch: tuple[str, ...]

    @property
    def consistent(self) -> bool:
        return not self.missing_in_replica and not self.hash_mismatch


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _relative_files(root: Path) -> dict[str, Path]:
    return {str(p.relative_to(root)).replace("\\", "/"): p for p in root.rglob("*") if p.is_file()}


def check_replica_consistency(primary_root: Path, replica_root: Path) -> ReplicaConsistencyReport:
    """比对主副本（D盘）与副副本（E盘）：文件集合 + sha256 逐一核对。"""
    primary = _relative_files(Path(primary_root))
    replica = _relative_files(Path(replica_root))
    missing = sorted(k for k in primary if k not in replica)
    mismatch = sorted(k for k in primary if k in replica and _sha256(primary[k]) != _sha256(replica[k]))
    matched = sum(1 for k in primary if k in replica and _sha256(primary[k]) == _sha256(replica[k]))
    return ReplicaConsistencyReport(
        matched=matched,
        missing_in_replica=tuple(missing),
        hash_mismatch=tuple(mismatch),
    )


# ---------------------------------------------------------------------------
# 5. RTO/RPO 分级目标（L1~L6）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RecoveryTarget:
    """单级恢复目标：RTO（恢复时长上限，分钟）/ RPO（数据丢失上限，秒）。"""

    rto_minutes: float
    rpo_seconds: float


@dataclass(frozen=True)
class DrillResult:
    """恢复演练判定结果。"""

    level: str
    passed: bool
    observed_rto_minutes: float
    observed_rpo_seconds: float
    target: RecoveryTarget


# 分级口径（候选注册表 CAND-DAT-006 problem 陈述：L1<5min/≤1s ~ L6<240min/≤24h）
RECOVERY_LEVELS: dict[str, RecoveryTarget] = {
    "L1": RecoveryTarget(rto_minutes=5, rpo_seconds=1),
    "L2": RecoveryTarget(rto_minutes=15, rpo_seconds=60),
    "L3": RecoveryTarget(rto_minutes=30, rpo_seconds=300),
    "L4": RecoveryTarget(rto_minutes=60, rpo_seconds=3600),
    "L5": RecoveryTarget(rto_minutes=120, rpo_seconds=14400),
    "L6": RecoveryTarget(rto_minutes=240, rpo_seconds=86400),
}


def main() -> None:
    """入口——待实现。"""


if __name__ == "__main__":
    main()
