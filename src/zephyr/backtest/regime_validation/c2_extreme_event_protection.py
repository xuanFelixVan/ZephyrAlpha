# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §4.3 C2 / §5
# [MODULE] zephyr.backtest.regime_validation.c2_extreme_event_protection
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan C2 极端事件回撤保护
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 只消费既有 C1 开/关回测净值产物, 不重跑回测; 窗口内 MaxDD=nav/cummax(nav)−1 最小值(负值); 改善=|DD_关|−|DD_开|; 样本<2 的窗口跳过并留痕; 全部跳过→抛错; frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] C2ProtectionError(ZA-BT-0030)
# [TESTS] tests/backtest/test_c2_extreme_event_protection.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: nav_baseline/nav_experiment(C1 开/关两组净值序列, pd.Series 日期索引, 既有回测产物)
# I2: crisis_windows(CRISIS 时段清单 (name,start,end)) + improvement_threshold=0.05(§5 C2)
# F1: max_drawdown_of(窗口净值切片→cummax 回撤序列最小值)
# A1: evaluate_extreme_event_protection(逐窗口开/关 MaxDD→改善→均值≥5pp 判定)
# O1: C2ProtectionReport(逐事件结果 + mean_improvement + passed + skipped 留痕)
# [/ALGO_FLOW]
"""
D_BACKTEST — C2 极端事件回撤保护分析（11 号 memo §4.3 C2）。

纯分析函数：不重跑回测，只消费 C1 既有开/关两组净值产物，定位历史
CRISIS 时段（memo §4.2 B4 案例库：2008-09/2015-08/2020-03/2024-07 等），
逐时段对比开/关 MaxDD，按 §5 C2 门槛「CRISIS 时段 MaxDD 改善 ≥5pp」判定。

依据: 11_regime_backtest_validation_plan §4.3 C2 / §5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: nav 参数
#   fields: 参数 nav，类型注解 Sequence[float]
#   code: c2_extreme_event_protection.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: nav_baseline 参数
#   fields: 参数 nav_baseline，类型注解 pd.Series
#   code: c2_extreme_event_protection.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: nav_experiment 参数
#   fields: 参数 nav_experiment，类型注解 pd.Series
#   code: c2_extreme_event_protection.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: crisis_windows 参数
#   fields: 参数 crisis_windows，类型注解 Sequence[tuple[Hashable, Hashable, Hash…
#   code: c2_extreme_event_protection.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① max_drawdown_of
#   name_en: max_drawdown_of
#   intro: 窗口净值 → MaxDD（负值；nav/cummax(nav)−1 最小值）。
#   desc: 窗口净值 → MaxDD（负值；nav/cummax(nav)−1 最小值）。单调上涨=0。；源码 L135-L143
#   inputs: nav
#   outputs: float
# - id: A2
#   name_zh: ② evaluate_extreme_event_protection
#   name_en: evaluate_extreme_event_protection
#   intro: C2 主入口：CRISIS 时段开/关 MaxDD 改善判定。
#   desc: C2 主入口：CRISIS 时段开/关 MaxDD 改善判定。 Args: nav_baseline / nav_experiment: C1 关/开两组净值序列（pd.Seri…；源码 L146-L212
#   inputs: nav_baseline nav_experiment crisis_windows improvement_threshold
#   outputs: C2ProtectionReport
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan C2 极端事件回撤保护
# - id: O2
#   name_zh: C2ProtectionReport
#   name_en: C2ProtectionReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan C2 极端事件回撤保护
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Hashable, Sequence

import numpy as np
import pandas as pd

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class C2ProtectionError(ZephyrBaseError):
    """ZA-BT-0030: C2 极端事件保护分析错误（输入非法/全部窗口无样本）。"""

    error_code = "ZA-BT-0030"


@dataclass(frozen=True)
class C2EventResult:
    """单 CRISIS 时段对比结果——不可变。MaxDD 为负值（-0.35=回撤 35%）。"""

    name: Hashable
    n_days: int
    dd_baseline: float  # 关（负值）
    dd_experiment: float  # 开（负值）
    improvement: float  # |dd_关| − |dd_开|（正值=节流保护了回撤）


@dataclass(frozen=True)
class C2ProtectionReport:
    """C2 极端事件保护报告——不可变。"""

    events: tuple[C2EventResult, ...]
    mean_improvement: float  # 各时段改善均值
    min_improvement: float  # 最差时段改善
    skipped: tuple[Hashable, ...]  # 样本<2 被跳过的时段名（留痕）
    passed: bool  # mean_improvement ≥ threshold（§5 C2=0.05）
    summary: str


def max_drawdown_of(nav: Sequence[float]) -> float:
    """窗口净值 → MaxDD（负值；nav/cummax(nav)−1 最小值）。单调上涨=0。"""
    arr = np.asarray(nav, dtype=float)
    if arr.size == 0 or arr[0] <= 0:
        return 0.0
    cummax = np.maximum.accumulate(arr)
    with np.errstate(divide="ignore", invalid="ignore"):
        dd = np.where(cummax > 0, arr / cummax - 1.0, 0.0)
    return float(dd.min())


def evaluate_extreme_event_protection(
    nav_baseline: pd.Series,
    nav_experiment: pd.Series,
    crisis_windows: Sequence[tuple[Hashable, Hashable, Hashable]],
    improvement_threshold: float = 0.05,
) -> C2ProtectionReport:
    """C2 主入口：CRISIS 时段开/关 MaxDD 改善判定。

    Args:
        nav_baseline / nav_experiment: C1 关/开两组净值序列（pd.Series，
            索引须支持 .loc[start:end] 切片，两组索引口径一致）。
        crisis_windows: [(name, start, end), ...] CRISIS 时段清单。
        improvement_threshold: 改善门槛（§5 C2=0.05 即 5pp）。

    Raises:
        C2ProtectionError: 净值非有限 / 窗口清单为空 / 全部窗口样本不足。
    """
    if not crisis_windows:
        raise C2ProtectionError("crisis_windows 不能为空")
    if improvement_threshold <= 0:
        raise C2ProtectionError(f"improvement_threshold 需 >0: {improvement_threshold}")
    for label, nav in (("baseline", nav_baseline), ("experiment", nav_experiment)):
        vals = np.asarray(nav.to_numpy(), dtype=float)
        if vals.size == 0 or not np.isfinite(vals).all():
            raise C2ProtectionError(f"nav_{label} 为空或含 NaN/Inf")

    events: list[C2EventResult] = []
    skipped: list[Hashable] = []
    for name, start, end in crisis_windows:
        base_win = nav_baseline.loc[start:end]
        exp_win = nav_experiment.loc[start:end]
        if len(base_win) < 2 or len(exp_win) < 2:
            skipped.append(name)
            _logger.warning("C2: 时段 %s 样本不足（base=%d/exp=%d），跳过", name, len(base_win), len(exp_win))
            continue
        dd_base = max_drawdown_of(base_win.to_numpy())
        dd_exp = max_drawdown_of(exp_win.to_numpy())
        events.append(
            C2EventResult(
                name=name,
                n_days=int(min(len(base_win), len(exp_win))),
                dd_baseline=dd_base,
                dd_experiment=dd_exp,
                improvement=abs(dd_base) - abs(dd_exp),
            )
        )

    if not events:
        raise C2ProtectionError("全部 CRISIS 时段样本不足，无法评估")
    improvements = [e.improvement for e in events]
    mean_imp = float(np.mean(improvements))
    min_imp = float(np.min(improvements))
    passed = mean_imp >= improvement_threshold
    summary = (
        f"C2 极端事件保护: {len(events)} 时段（跳过 {len(skipped)}）, "
        f"MaxDD改善 mean={mean_imp:+.2%} min={min_imp:+.2%} "
        f"门槛≥{improvement_threshold:.0%} → {'通过' if passed else '不通过（CRISIS 保护失效）'}"
    )
    _logger.info("C2 完成: %s", summary)
    return C2ProtectionReport(
        events=tuple(events),
        mean_improvement=mean_imp,
        min_improvement=min_imp,
        skipped=tuple(skipped),
        passed=passed,
        summary=summary,
    )


__all__ = [
    "C2EventResult",
    "C2ProtectionError",
    "C2ProtectionReport",
    "evaluate_extreme_event_protection",
    "max_drawdown_of",
]
