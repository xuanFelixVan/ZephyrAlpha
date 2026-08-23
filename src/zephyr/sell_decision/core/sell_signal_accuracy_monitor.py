# [BLUEPRINT] MOD-SELL-010 | docs/03_modules/MOD-SELL-010/
# [MODULE] zephyr.sell_decision.core.sell_signal_accuracy_monitor
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.sell_decision.core.sell_signal_collector ; zephyr.sell_decision.core.sell_signal_scorer ; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SELL-002(准确率统计回喂评分) ; MOD-SELL-011(AB测试输入) ; D_RISK
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按信号类型聚合命中率(产出复用MOD-SELL-002 AccuracyStat); 衰退=样本≥min_samples且命中率<baseline−tolerance; 小样本不判衰退(防误报); 监控只评估不改动信号源(三维解耦); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-010/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidAccuracyRecordError(ZA-SELL-0025)
# [TESTS] tests/sell_decision/test_sell_signal_accuracy_monitor.py
# [A_module] module_id=MOD-SELL-010 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Sell Signal Accuracy Monitor — 卖出信号准确度监控 (MOD-SELL-010)

闭环复盘（宪章 §1.1 自我迭代）：聚合信号的事后兑现记录，产出两类
东西：

  1. **按信号类型的命中率统计**——直接复用 MOD-SELL-002 的
     AccuracyStat，回喂评分器做准确率调整（自我迭代闭环）；
  2. **衰退预警**——某类信号在样本充足（≥min_samples）时命中率低于
     基线−容差 → degraded_types + warnings（提示该信号源可能失效，
     供 AB 测试/退役决策参考）。

监控只评估、不改动信号源（与具体选股策略零耦合）。

纪律：纯函数、无 IO；兑现记录由调用方注入（禁自造数据管道）。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Final

from zephyr.sell_decision.core.sell_signal_collector import SellSignalType
from zephyr.sell_decision.core.sell_signal_scorer import AccuracyStat
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "AccuracyMonitorReport",
    "InvalidAccuracyRecordError",
    "SignalOutcomeRecord",
    "evaluate_accuracy",
]

_DEFAULT_BASELINE_RATE: Final = 0.5
_DEFAULT_TOLERANCE: Final = 0.10
_DEFAULT_MIN_SAMPLES: Final = 30


class InvalidAccuracyRecordError(ZephyrBaseError):
    """准确度监控输入非法（信号类型错误/基线/容差/样本门槛越界）。"""

    error_code = "ZA-SELL-0025"


@dataclass(frozen=True)
class SignalOutcomeRecord:
    """单条信号事后兑现记录。

    Attributes:
        signal_type: 信号类型（8 类之一）
        hit: 是否兑现（信号触发后按预期方向走出）
    """

    signal_type: SellSignalType
    hit: bool


@dataclass(frozen=True)
class AccuracyMonitorReport:
    """准确度监控报告（frozen 不可变）。

    Attributes:
        by_type: {SellSignalType: AccuracyStat}（回喂 MOD-SELL-002）
        overall_hits: 总命中
        overall_total: 总样本
        overall_rate: 总体命中率（0 样本=0.0）
        degraded_types: 衰退信号类型（按枚举名排序）
        warnings: 预警留痕
    """

    by_type: dict[SellSignalType, AccuracyStat]
    overall_hits: int
    overall_total: int
    overall_rate: float
    degraded_types: tuple[SellSignalType, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)


def evaluate_accuracy(
    records: Sequence[SignalOutcomeRecord],
    *,
    baseline_rate: float = _DEFAULT_BASELINE_RATE,
    degradation_tolerance: float = _DEFAULT_TOLERANCE,
    min_samples: int = _DEFAULT_MIN_SAMPLES,
) -> AccuracyMonitorReport:
    """评估卖出信号准确度（纯函数）。

    Args:
        records: 事后兑现记录序列
        baseline_rate: 命中率基线 ∈[0,1]（默认 0.5）
        degradation_tolerance: 衰退容差 ∈[0,1]（默认 0.10）
        min_samples: 衰退判定最小样本数 ≥1（默认 30）

    Returns:
        AccuracyMonitorReport

    Raises:
        InvalidAccuracyRecordError: 输入非法
    """
    for name, v in (("baseline_rate", baseline_rate), ("degradation_tolerance", degradation_tolerance)):
        if not math.isfinite(v) or not (0.0 <= v <= 1.0):
            raise InvalidAccuracyRecordError(f"{name} 非法（须 ∈[0,1]），got {v}")
    if min_samples < 1:
        raise InvalidAccuracyRecordError(f"min_samples 非法（须 ≥1），got {min_samples}")

    hits: dict[SellSignalType, int] = {}
    totals: dict[SellSignalType, int] = {}
    for rec in records:
        if not isinstance(rec.signal_type, SellSignalType):
            raise InvalidAccuracyRecordError(
                f"signal_type 须为 SellSignalType，got {rec.signal_type!r}"
            )
        totals[rec.signal_type] = totals.get(rec.signal_type, 0) + 1
        if rec.hit:
            hits[rec.signal_type] = hits.get(rec.signal_type, 0) + 1

    by_type = {
        st: AccuracyStat(hits=hits.get(st, 0), total=totals[st]) for st in sorted(totals, key=lambda x: x.value)
    }

    overall_hits = sum(hits.values())
    overall_total = sum(totals.values())
    overall_rate = overall_hits / overall_total if overall_total > 0 else 0.0

    degraded: list[SellSignalType] = []
    warnings: list[str] = []
    for st in sorted(by_type, key=lambda x: x.value):
        stat = by_type[st]
        if stat.total < min_samples:
            continue
        rate = stat.hits / stat.total
        if rate < baseline_rate - degradation_tolerance:
            degraded.append(st)
            warnings.append(
                f"信号类型 {st.value} 命中率 {rate:.2%} 低于基线 {baseline_rate:.2%}"
                f"−容差 {degradation_tolerance:.2%}（n={stat.total}），疑似失效"
            )

    return AccuracyMonitorReport(
        by_type=by_type,
        overall_hits=overall_hits,
        overall_total=overall_total,
        overall_rate=overall_rate,
        degraded_types=tuple(degraded),
        warnings=tuple(warnings),
    )
