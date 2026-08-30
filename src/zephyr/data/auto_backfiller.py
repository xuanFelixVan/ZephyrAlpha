# [BLUEPRINT] MOD-DAT-AUTO-BACKFILLER | docs/03_modules/_domain_data/auto_backfiller/blueprint.md
# [MODULE] zephyr.data.auto_backfiller
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（判定核心纯内存；executor/sink 全注入）
# [CONSUMERS] 运行时装配批（触发事件装配 / executor 接因子重算 / lineage_sink 接血缘真源 / retrain_sink 接 auto-retrain）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 触发事件 Fail-Closed 校验；按日期分片规划；抽样确定性（同种子同样本）；血缘与重训只在全成功+样本通过时触发；sink 异常不阻断报告
# [MODIFY-GUARD] docs/03_modules/_domain_data/auto_backfiller/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知触发类型/日期倒挂/空target→ValueError；executor异常→该分片failed不中断；sink异常→sink_errors留痕
# [TESTS] tests/zephyr/data/test_auto_backfiller.py
# [A_module] module_id=MOD-DAT-AUTO-BACKFILLER | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



AutoBackfiller — 事件触发式自动回填器（MOD-DAT-AUTO-BACKFILLER）

B10-01815（AUD-DRAFT-001-DIGEST P1 波 W-P1-09，§29.2-7）：输入触发事件
（新因子上线 new_factor / 公式升级 formula_upgrade / 数据源修复
data_source_fix），按日期分片规划回填，经注入 executor 逐分片执行，
10% 随机抽样验证，全部通过后更新血缘并触发 auto-retrain。

查重裁定：不复制 MOD-L00-004 backfill_checker（L10 周末行情缺口检测+
精准补下载，定时/数据面向）逻辑；本模块为因子/公式/数据源修复**事件**
触发的回填编排，缺口语义对齐走设计边。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: auto_backfiller.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: executor 参数
#   fields: 参数 executor（无注解）
#   code: auto_backfiller.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: trading_days_provider 参数
#   fields: 参数 trading_days_provider（无注解）
#   code: auto_backfiller.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: sample_validator 参数
#   fields: 参数 sample_validator（无注解）
#   code: auto_backfiller.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AutoBackfiller
#   name_en: AutoBackfiller
#   intro: 事件触发式自动回填器（判定核心纯内存，执行体/外发全注入）。
#   desc: 事件触发式自动回填器（判定核心纯内存，执行体/外发全注入）。；公共方法（定义序）: plan, run；源码 L160-L297
#   inputs: config executor trading_days_provider sample_validator lineage_sink r…
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: AutoBackfiller
#   downstream: 运行时装配批（触发事件装配 / executor 接因子重算 / lineage_sink 接血缘真源 / retrain_sink 接 auto-retra…
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
import random
from dataclasses import dataclass, field
from typing import Callable, Final, Optional

log = logging.getLogger(__name__)

__all__: Final = [
    "AutoBackfillConfig",
    "AutoBackfiller",
    "BackfillPlan",
    "BackfillReport",
    "BackfillShard",
    "BackfillTrigger",
    "ShardResult",
]

TRIGGER_TYPES: Final = ("new_factor", "formula_upgrade", "data_source_fix")


@dataclass(frozen=True)
class BackfillTrigger:
    """回填触发事件。"""

    trigger_type: str
    target: str
    start_date: datetime.date
    end_date: datetime.date


@dataclass(frozen=True)
class BackfillShard:
    """日期分片。"""

    shard_id: int
    start_date: datetime.date
    end_date: datetime.date


@dataclass(frozen=True)
class ShardResult:
    """单分片执行结果（executor 返回）。"""

    shard_id: int
    rows_written: int
    success: bool
    error: str = ""


@dataclass(frozen=True)
class BackfillPlan:
    """回填计划。"""

    trigger: BackfillTrigger
    shards: tuple[BackfillShard, ...]
    sample_ratio: float
    max_workers: int


@dataclass(frozen=True)
class BackfillReport:
    """回填报告。"""

    trigger: BackfillTrigger
    total_shards: int
    succeeded: int
    failed: int
    sampled: int
    sample_passed: bool
    lineage_updated: bool
    retrain_triggered: bool
    sink_errors: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AutoBackfillConfig:
    """配置。"""

    shard_days: int = 7
    sample_ratio: float = 0.10
    max_workers: int = 4


class AutoBackfiller:
    """事件触发式自动回填器（判定核心纯内存，执行体/外发全注入）。"""

    def __init__(
        self,
        config: AutoBackfillConfig | None = None,
        executor: Callable[[BackfillShard], ShardResult] | None = None,
        trading_days_provider: Callable[[datetime.date, datetime.date], list] | None = None,
        sample_validator: Callable[[BackfillShard, ShardResult], bool] | None = None,
        lineage_sink: Callable[[BackfillReport], None] | None = None,
        retrain_sink: Callable[[BackfillTrigger], None] | None = None,
        rng_seed: int | None = None,
    ) -> None:
        self._config = config or AutoBackfillConfig()
        if self._config.shard_days <= 0:
            raise ValueError("shard_days 必须为正整数")
        if not 0 < self._config.sample_ratio <= 1:
            raise ValueError("sample_ratio 须在 (0, 1]")
        self._executor = executor
        self._trading_days_provider = trading_days_provider
        self._sample_validator = sample_validator or self._default_validator
        self._lineage_sink = lineage_sink
        self._retrain_sink = retrain_sink
        self._rng = random.Random(rng_seed)

    # ── 校验 ──

    @staticmethod
    def _validate_trigger(trigger: BackfillTrigger) -> None:
        if trigger.trigger_type not in TRIGGER_TYPES:
            raise ValueError(f"未知触发类型: {trigger.trigger_type!r}（合法: {TRIGGER_TYPES}）")
        if not trigger.target:
            raise ValueError("target 不能为空")
        if trigger.start_date > trigger.end_date:
            raise ValueError(f"日期倒挂: {trigger.start_date} > {trigger.end_date}")

    # ── 规划 ──

    def plan(self, trigger: BackfillTrigger) -> BackfillPlan:
        """校验触发事件并按 shard_days 切日期分片（可选交易日历过滤）。"""
        self._validate_trigger(trigger)
        cfg = self._config
        if self._trading_days_provider is not None:
            days = sorted(self._trading_days_provider(trigger.start_date, trigger.end_date))
        else:
            n = (trigger.end_date - trigger.start_date).days
            days = [trigger.start_date + datetime.timedelta(days=i) for i in range(n + 1)]
        shards: list[BackfillShard] = []
        for i in range(0, len(days), cfg.shard_days):
            chunk = days[i : i + cfg.shard_days]
            shards.append(
                BackfillShard(
                    shard_id=len(shards),
                    start_date=chunk[0],
                    end_date=chunk[-1],
                )
            )
        return BackfillPlan(
            trigger=trigger,
            shards=tuple(shards),
            sample_ratio=cfg.sample_ratio,
            max_workers=cfg.max_workers,
        )

    # ── 执行 ──

    @staticmethod
    def _default_validator(shard: BackfillShard, result: ShardResult) -> bool:
        return result.success and result.rows_written > 0

    def run(self, trigger: BackfillTrigger) -> BackfillReport:
        """逐分片执行 + 抽样验证 + 血缘/重训触发（fail-closed）。"""
        if self._executor is None:
            raise ValueError("executor 未注入，无法执行回填")
        plan = self.plan(trigger)
        results: list[ShardResult] = []
        for shard in plan.shards:
            try:
                results.append(self._executor(shard))
            except Exception as exc:  # noqa: BLE001 — 单片失败不中断其余
                log.warning("分片 %s 执行异常: %s", shard.shard_id, exc)
                results.append(ShardResult(shard_id=shard.shard_id, rows_written=0, success=False, error=str(exc)))
        succeeded = sum(1 for r in results if r.success)
        failed = len(results) - succeeded

        # 抽样验证：确定性抽样（最少 1 片）
        ok_results = [r for r in results if r.success]
        n_sample = max(1, round(len(ok_results) * plan.sample_ratio)) if ok_results else 0
        sampled = self._rng.sample(ok_results, k=min(n_sample, len(ok_results))) if ok_results else []
        shard_by_id = {s.shard_id: s for s in plan.shards}
        sample_passed = all(self._sample_validator(shard_by_id[r.shard_id], r) for r in sampled) if sampled else False

        # 血缘+重训：全成功且样本通过才触发；sink 异常留痕不阻断
        sink_errors: list[str] = []
        lineage_updated = False
        retrain_triggered = False
        all_ok = failed == 0 and sample_passed and bool(results)
        report = BackfillReport(
            trigger=trigger,
            total_shards=len(results),
            succeeded=succeeded,
            failed=failed,
            sampled=len(sampled),
            sample_passed=sample_passed,
            lineage_updated=False,
            retrain_triggered=False,
            sink_errors=(),
        )
        if all_ok:
            if self._lineage_sink is not None:
                try:
                    self._lineage_sink(report)
                    lineage_updated = True
                except Exception as exc:  # noqa: BLE001
                    log.warning("lineage_sink 异常: %s", exc)
                    sink_errors.append(f"lineage_sink: {exc}")
            else:
                lineage_updated = True
            if self._retrain_sink is not None:
                try:
                    self._retrain_sink(trigger)
                    retrain_triggered = True
                except Exception as exc:  # noqa: BLE001
                    log.warning("retrain_sink 异常: %s", exc)
                    sink_errors.append(f"retrain_sink: {exc}")
            else:
                retrain_triggered = True
        return BackfillReport(
            trigger=trigger,
            total_shards=len(results),
            succeeded=succeeded,
            failed=failed,
            sampled=len(sampled),
            sample_passed=sample_passed,
            lineage_updated=lineage_updated,
            retrain_triggered=retrain_triggered,
            sink_errors=tuple(sink_errors),
        )
