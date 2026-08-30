# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §0.6.3 现成该跑 / §4.3 C4 / §5
# [MODULE] zephyr.backtest.regime_validation.c4_deflated_sharpe_runner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.simulation.deflated_sharpe_calculator; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan C4 统计显著性(BM-BT-05-G)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 零新计算: DSR 全委托既有 DeflatedSharpeCalculator(本模块只编排+封装); 输入=既有回测收益序列产物(离线跑批,不触发真实回测); num_trials 默认=变体数(多重比较修正); frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] C4DeflatedSharpeError(ZA-BT-0032)
# [TESTS] tests/backtest/test_c4_deflated_sharpe_runner.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: returns_by_variant(变体名→逐期收益序列, 既有回测产物, 如 Shrinkage 开/关/参数网格各点)
# I2: DSRConfig(可选) + num_trials(默认=变体数, memo §0.6.3: 测了 N 个变体后 Sharpe 要打折)
# A1: run_deflated_sharpe_batch(逐变体调 DeflatedSharpeCalculator.calculate→年化Sharpe最优者裁定)
# O1: C4BatchReport(逐变体 DSR + best_variant + is_significant + passed)
# [/ALGO_FLOW]
"""
D_BACKTEST — C4 Deflated Sharpe 跑批封装入口（11 号 memo §0.6.3 / §4.3 C4）。

对既有回测收益序列产物（如 Shrinkage 开/关两组、参数网格各变体）批量
计算 Deflated Sharpe Ratio——多重比较修正（测了 N 个变体取最优，Sharpe
要打折，Bailey & López de Prado 2014；mathandmarkets 2026-05 背书）。

零新计算：DSR 数学全委托既有 zephyr.simulation.deflated_sharpe_calculator
（MOD-SIM-024），本模块只做跑批编排与最优变体裁定。只做封装+测试，
不执行真实数据跑批（真实跑批待首批策略回测资源排期，memo §10.5 待裁定#1）。

依据: 11_regime_backtest_validation_plan §0.6.3 / §4.3 C4 / §5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: returns_by_variant 参数
#   fields: 参数 returns_by_variant，类型注解 Mapping[str, Sequence[float]]
#   code: c4_deflated_sharpe_runner.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config，类型注解 DSRConfig | None
#   code: c4_deflated_sharpe_runner.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: num_trials 参数
#   fields: 参数 num_trials，类型注解 int | None
#   code: c4_deflated_sharpe_runner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_deflated_sharpe_batch
#   name_en: run_deflated_sharpe_batch
#   intro: C4 主入口：多变体收益序列的 DSR 批量计算与最优裁定。
#   desc: C4 主入口：多变体收益序列的 DSR 批量计算与最优裁定。 Args: returns_by_variant: {变体名: 逐期收益序列}（每个 ≥3 样本，有限值）。 con…；源码 L127-L197
#   inputs: returns_by_variant config num_trials
#   outputs: C4BatchReport
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: C4BatchReport
#   name_en: C4BatchReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan C4 统计显著性(BM-BT-05-G)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from zephyr.simulation.deflated_sharpe_calculator import (
    DeflatedSharpeCalculator,
    DSRConfig,
    SimulationError,
)

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class C4DeflatedSharpeError(ZephyrBaseError):
    """ZA-BT-0032: C4 DSR 跑批封装错误（输入非法/计算器异常）。"""

    error_code = "ZA-BT-0032"


@dataclass(frozen=True)
class C4VariantDSR:
    """单变体 DSR 结果——不可变。"""

    name: str
    sharpe_annualized: float
    dsr: float  # ∈(0,1)，多重比较修正后
    is_significant: bool  # dsr ≥ config.significance_threshold


@dataclass(frozen=True)
class C4BatchReport:
    """C4 DSR 跑批报告——不可变。"""

    num_variants: int
    num_trials: int  # 多重比较试次数（默认=变体数）
    variants: tuple[C4VariantDSR, ...]  # 按年化 Sharpe 降序
    best_variant: str
    best_sharpe: float
    best_dsr: float
    is_significant: bool  # 最优变体 DSR 是否显著
    passed: bool  # = is_significant（§5 C4: 效果不显著=可能运气）
    summary: str


def run_deflated_sharpe_batch(
    returns_by_variant: Mapping[str, Sequence[float]],
    config: DSRConfig | None = None,
    num_trials: int | None = None,
) -> C4BatchReport:
    """C4 主入口：多变体收益序列的 DSR 批量计算与最优裁定。

    Args:
        returns_by_variant: {变体名: 逐期收益序列}（每个 ≥3 样本，有限值）。
        config: DSRConfig（None=calculator 默认：显著性 0.95 / 252 年化 / rf=0）。
        num_trials: 多重比较试次数；None=变体数（memo §0.6.3 裁定口径）。

    Returns:
        C4BatchReport；passed = 最优变体 DSR 达显著性阈值。

    Raises:
        C4DeflatedSharpeError: 空变体集 / 序列<3 / 含非有限值 / num_trials<1 /
            calculator 计算异常。
    """
    if not returns_by_variant:
        raise C4DeflatedSharpeError("returns_by_variant 不能为空")
    n_variants = len(returns_by_variant)
    trials = n_variants if num_trials is None else int(num_trials)
    if trials < 1:
        raise C4DeflatedSharpeError(f"num_trials 需 ≥1: {trials}")

    cleaned: dict[str, list[float]] = {}
    for name, series in returns_by_variant.items():
        arr = np.asarray(list(series), dtype=float)
        if arr.size < 3:
            raise C4DeflatedSharpeError(f"变体 {name} 样本不足: {arr.size} < 3")
        if not np.isfinite(arr).all():
            raise C4DeflatedSharpeError(f"变体 {name} 收益序列含 NaN/Inf")
        cleaned[str(name)] = arr.tolist()

    calc = DeflatedSharpeCalculator(config)
    variants: list[C4VariantDSR] = []
    for name, rets in cleaned.items():
        try:
            res = calc.calculate(rets, num_trials=trials)
        except SimulationError as exc:
            raise C4DeflatedSharpeError(f"变体 {name} DSR 计算失败: {exc}") from exc
        variants.append(
            C4VariantDSR(
                name=name,
                sharpe_annualized=res.sharpe_annualized,
                dsr=res.dsr,
                is_significant=res.is_significant,
            )
        )
    variants.sort(key=lambda v: (-v.sharpe_annualized, v.name))

    best = variants[0]
    threshold = (config or DSRConfig()).significance_threshold
    summary = (
        f"C4 Deflated Sharpe 跑批: {n_variants} 变体, num_trials={trials}, "
        f"最优={best.name} 年化Sharpe={best.sharpe_annualized:.4f} DSR={best.dsr:.4f} "
        f"显著性门槛≥{threshold} → {'显著' if best.is_significant else '不显著（可能运气）'}"
    )
    _logger.info("C4 完成: %s", summary)
    return C4BatchReport(
        num_variants=n_variants,
        num_trials=trials,
        variants=tuple(variants),
        best_variant=best.name,
        best_sharpe=best.sharpe_annualized,
        best_dsr=best.dsr,
        is_significant=best.is_significant,
        passed=best.is_significant,
        summary=summary,
    )


__all__ = [
    "C4BatchReport",
    "C4DeflatedSharpeError",
    "C4VariantDSR",
    "run_deflated_sharpe_batch",
]
