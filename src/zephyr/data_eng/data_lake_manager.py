# [BLUEPRINT] MOD-DATENG-006 | docs/03_modules/_domain_data_eng/data_lake_manager/blueprint.md
# [MODULE] zephyr.data_eng.data_lake_manager
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] 无（编排核心纯内存；migrate/purge/compress 执行器与 clock/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（层间迁移挂调度 / 保留清理接存储执行器 / 压缩归档接 Parquet 写入器）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三层词表闭合(hot|warm|cold); 迁移仅逐层向下(hot→warm→cold); 层策略注册表闭合(未注册层不参与裁决); 计划按数据集名确定性排序; 保留清理仅裁决cold层超期数据集; 压缩编排仅cold层未压缩数据集; 执行全经注入回调; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_eng/data_lake_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DataLakeError(占位 ZA-DE-UNREGISTERED-DATA-LAKE)——空数据集名/非法策略/重复注册/未知数据集/未来时间戳/执行器缺失时抛
# [TESTS] tests/data_eng/test_data_lake_manager.py
# [A_module] module_id=MOD-DATENG-006 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
DataLakeManager — 数据湖三层管理器（MOD-DATENG-006）。

B5-07240（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATENG-009，B5）：热层
（ClickHouse 近 30 天）/温层（本地 Parquet）/冷层（归档 ZSTD）三层策略
注册表 + 数据迁移调度计划（层间迁移任务生成）+ 保留策略执行（过期清理
裁决）+ 自动压缩归档编排——迁移/清理/压缩执行全注入回调。

边界声明（蓝图 §0）：tiered_storage（D_GOV_AUDIT）为通用分层存储语义件
——本件是数据湖三层**编排**（计划/裁决），不实现存储引擎；cold_data_
archive_manager（MOD-DATENG-002）管 CH 分区→Parquet 归档索引，本件管数
据集级层间迁移/保留/压缩裁决，索引归前者，编排归后者。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: data_lake_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: migrate_executor 参数
#   fields: 参数 migrate_executor（无注解）
#   code: data_lake_manager.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: purge_executor 参数
#   fields: 参数 purge_executor（无注解）
#   code: data_lake_manager.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: compress_executor 参数
#   fields: 参数 compress_executor（无注解）
#   code: data_lake_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DataLakeManager
#   name_en: DataLakeManager
#   intro: 数据湖三层编排件（策略注册表 + 迁移/清理/压缩计划与执行）。
#   desc: 数据湖三层编排件（策略注册表 + 迁移/清理/压缩计划与执行）。；公共方法（定义序）: register_tier_policy, register_dataset, plan_migrations, run_migr…
#   inputs: clock migrate_executor purge_executor compress_executor alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: DataLakeManager
#   downstream: 运行时装配批（层间迁移挂调度 / 保留清理接存储执行器 / 压缩归档接 Parquet 写入器）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "CompressionTask",
    "DataLakeError",
    "DataLakeManager",
    "DatasetState",
    "LakeTier",
    "MigrationTask",
    "PurgeDecision",
    "TierPolicy",
]

_SECONDS_PER_DAY: Final = 86400.0

_NEXT_TIER: Final[dict[LakeTier, LakeTier]] = {}


class DataLakeError(Exception):
    """数据湖分层编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DE-UNREGISTERED-DATA-LAKE。
    """


class LakeTier(str, Enum):
    """数据湖层（词表闭合）。"""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


_NEXT_TIER.update(
    {
        LakeTier.HOT: LakeTier.WARM,
        LakeTier.WARM: LakeTier.COLD,
    }
)


@dataclass(frozen=True)
class TierPolicy:
    """层策略：max_age_days 超龄迁出（COLD 层语义=保留期，超期清理）；codec=归档压缩编码。"""

    tier: LakeTier
    max_age_days: int
    codec: str = "zstd"


@dataclass(frozen=True)
class DatasetState:
    """数据集登记观测（frozen）。"""

    name: str
    tier: LakeTier
    oldest_data_at: datetime.datetime
    size_bytes: int = 0
    compressed: bool = False


@dataclass(frozen=True)
class MigrationTask:
    """层间迁移任务（逐层向下）。"""

    dataset: str
    from_tier: LakeTier
    to_tier: LakeTier
    planned_at: datetime.datetime
    reason: str


@dataclass(frozen=True)
class PurgeDecision:
    """保留策略清理裁决（COLD 层超保留期）。"""

    dataset: str
    tier: LakeTier
    decided_at: datetime.datetime
    reason: str


@dataclass(frozen=True)
class CompressionTask:
    """自动压缩归档任务（COLD 层未压缩数据集）。"""

    dataset: str
    tier: LakeTier
    codec: str
    planned_at: datetime.datetime


@dataclass
class _LakeRecord:
    tier: LakeTier
    oldest_data_at: datetime.datetime
    size_bytes: int
    compressed: bool


class DataLakeManager:
    """数据湖三层编排件（策略注册表 + 迁移/清理/压缩计划与执行）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        migrate_executor: Callable[[MigrationTask], None] | None = None,
        purge_executor: Callable[[PurgeDecision], None] | None = None,
        compress_executor: Callable[[CompressionTask], None] | None = None,
        alert_sink: Callable[[str], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._migrate_executor = migrate_executor
        self._purge_executor = purge_executor
        self._compress_executor = compress_executor
        self._alert_sink = alert_sink
        self._policies: dict[LakeTier, TierPolicy] = {}
        self._datasets: dict[str, _LakeRecord] = {}

    # ── 策略与数据集注册 ──────────────────────────────────────────────────

    def register_tier_policy(self, policy: TierPolicy) -> None:
        """层策略注册：tier 唯一，max_age_days>0；COLD 层 max_age_days 即保留期。"""
        if not isinstance(policy.tier, LakeTier):
            raise DataLakeError(f"非法层: {policy.tier!r}")
        if policy.max_age_days <= 0:
            raise DataLakeError(f"max_age_days 非法: {policy.max_age_days}")
        if not policy.codec:
            raise DataLakeError("codec 为空")
        if policy.tier in self._policies:
            raise DataLakeError(f"层策略重复注册: {policy.tier.value!r}")
        self._policies[policy.tier] = policy

    def register_dataset(self, state: DatasetState) -> None:
        """数据集登记：name 唯一，oldest_data_at 不得晚于当前时刻。"""
        if not state.name:
            raise DataLakeError("数据集 name 为空")
        if not isinstance(state.tier, LakeTier):
            raise DataLakeError(f"非法层: {state.tier!r}")
        if state.size_bytes < 0:
            raise DataLakeError(f"size_bytes 非法: {state.size_bytes}")
        if state.oldest_data_at > self._clock():
            raise DataLakeError(f"oldest_data_at 晚于当前时刻: {state.name!r}")
        if state.name in self._datasets:
            raise DataLakeError(f"数据集重复注册: {state.name!r}")
        self._datasets[state.name] = _LakeRecord(
            tier=state.tier,
            oldest_data_at=state.oldest_data_at,
            size_bytes=state.size_bytes,
            compressed=state.compressed,
        )

    # ── 迁移调度计划 ──────────────────────────────────────────────────────

    def plan_migrations(self) -> tuple[MigrationTask, ...]:
        """迁移计划：数据集龄超本层 max_age_days → 逐层向下迁移（按名排序）。"""
        now = self._clock()
        tasks: list[MigrationTask] = []
        for name in sorted(self._datasets):
            rec = self._datasets[name]
            policy = self._policies.get(rec.tier)
            if policy is None:
                continue  # 层策略未注册：不参与裁决（注册表闭合）
            target = _NEXT_TIER.get(rec.tier)
            if target is None:
                continue  # COLD 层无下游（保留清理由 plan_purge 裁决）
            age_days = (now - rec.oldest_data_at).total_seconds() / _SECONDS_PER_DAY
            if age_days > policy.max_age_days:
                tasks.append(
                    MigrationTask(
                        dataset=name,
                        from_tier=rec.tier,
                        to_tier=target,
                        planned_at=now,
                        reason=(f"数据龄 {age_days:.2f}d 超 {rec.tier.value} 层上限 {policy.max_age_days}d"),
                    )
                )
        return tuple(tasks)

    def run_migrations(self) -> tuple[MigrationTask, ...]:
        """迁移执行：计划 → 注入 migrate_executor 逐任务执行 → 层状态推进。"""
        if self._migrate_executor is None:
            raise DataLakeError("migrate_executor 未注入（迁移执行强制注入回调）")
        tasks = self.plan_migrations()
        for task in tasks:
            self._migrate_executor(task)
            rec = self._datasets[task.dataset]
            if rec.tier is not task.from_tier:  # pragma: no cover — 同源防御
                raise DataLakeError(f"迁移状态漂移: {task.dataset!r}")
            rec.tier = task.to_tier
            _log.info("数据集迁移: %s %s→%s", task.dataset, task.from_tier.value, task.to_tier.value)
        return tasks

    # ── 保留策略执行 ──────────────────────────────────────────────────────

    def plan_purge(self) -> tuple[PurgeDecision, ...]:
        """清理裁决：COLD 层数据集龄超保留期 → 应清理（按名排序）。"""
        now = self._clock()
        cold_policy = self._policies.get(LakeTier.COLD)
        decisions: list[PurgeDecision] = []
        if cold_policy is None:
            return ()
        for name in sorted(self._datasets):
            rec = self._datasets[name]
            if rec.tier is not LakeTier.COLD:
                continue
            age_days = (now - rec.oldest_data_at).total_seconds() / _SECONDS_PER_DAY
            if age_days > cold_policy.max_age_days:
                decisions.append(
                    PurgeDecision(
                        dataset=name,
                        tier=rec.tier,
                        decided_at=now,
                        reason=(f"冷层数据龄 {age_days:.2f}d 超保留期 {cold_policy.max_age_days}d"),
                    )
                )
        return tuple(decisions)

    def run_purge(self) -> tuple[PurgeDecision, ...]:
        """清理执行：裁决 → 注入 purge_executor 物理清理 → 数据集除名。"""
        if self._purge_executor is None:
            raise DataLakeError("purge_executor 未注入（清理执行强制注入回调）")
        decisions = self.plan_purge()
        for decision in decisions:
            self._purge_executor(decision)
            del self._datasets[decision.dataset]
            self._alert(f"数据湖冷层清理: {decision.dataset}（{decision.reason}）")
        return decisions

    # ── 自动压缩归档编排 ──────────────────────────────────────────────────

    def plan_compression(self) -> tuple[CompressionTask, ...]:
        """压缩计划：COLD 层未压缩数据集 → 按冷层策略 codec 生成压缩任务。"""
        now = self._clock()
        cold_policy = self._policies.get(LakeTier.COLD)
        tasks: list[CompressionTask] = []
        if cold_policy is None:
            return ()
        for name in sorted(self._datasets):
            rec = self._datasets[name]
            if rec.tier is LakeTier.COLD and not rec.compressed:
                tasks.append(
                    CompressionTask(
                        dataset=name,
                        tier=rec.tier,
                        codec=cold_policy.codec,
                        planned_at=now,
                    )
                )
        return tuple(tasks)

    def run_compression(self) -> tuple[CompressionTask, ...]:
        """压缩执行：计划 → 注入 compress_executor 逐任务执行 → 压缩标记。"""
        if self._compress_executor is None:
            raise DataLakeError("compress_executor 未注入（压缩执行强制注入回调）")
        tasks = self.plan_compression()
        for task in tasks:
            self._compress_executor(task)
            self._datasets[task.dataset].compressed = True
            _log.info("数据集压缩归档: %s codec=%s", task.dataset, task.codec)
        return tasks

    # ── 只读检索 ──────────────────────────────────────────────────────────

    def dataset(self, name: str) -> DatasetState:
        """单数据集状态查询（未知 → Fail-Closed）。"""
        rec = self._datasets.get(name)
        if rec is None:
            raise DataLakeError(f"未知数据集: {name!r}")
        return DatasetState(
            name=name,
            tier=rec.tier,
            oldest_data_at=rec.oldest_data_at,
            size_bytes=rec.size_bytes,
            compressed=rec.compressed,
        )

    def list_datasets(self, tier: LakeTier | None = None) -> tuple[DatasetState, ...]:
        """数据集清单（按名确定性排序；可按层过滤）。"""
        return tuple(
            self.dataset(name) for name in sorted(self._datasets) if tier is None or self._datasets[name].tier is tier
        )

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, message: str) -> None:
        _log.warning("数据湖告警: %s", message)
        if self._alert_sink is not None:
            try:
                self._alert_sink(message)
            except Exception:  # noqa: BLE001 — 告警不阻断
                _log.exception("alert_sink 告警失败")
