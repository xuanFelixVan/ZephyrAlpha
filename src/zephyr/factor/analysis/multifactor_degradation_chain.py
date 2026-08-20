# [BLUEPRINT] MOD-L02-011 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-10
# [MODULE] zephyr.factor.analysis.multifactor_degradation_chain
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.multifactor_synthesis; numpy; pandas
# [CONSUMERS] multifactor_pit_backtest
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——IC历史仅含决策日之前观测; 回归仅在回测外启用(回测注入forward_returns=None)
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入->等权兜底; 任何分支不满足->逐级降级不抛错
# [TESTS] tests/factor/test_multifactor_degradation_chain.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: factor_panel(dict[str, pd.Series] 因子值面板) + ic_history(dict[str, list[float]] 历史IC) + forward_returns(可选前向收益)
# I2: DegradationChainParams(ic_min_samples=20/concentration=0.70/ic_abs_floor=0.02/regression_min_obs=120/condition_number_max=50)
# F1: decide(回归可行性→IC加权→等权兜底 三级降级决策, 输出SynthesisDecision(method+reason+ic_weights))
# A1: 回归分支(forward_returns≥120 且 条件数<50→regression; 条件数≥50→降IC加权)
# A2: IC加权分支(样本≥20: 全池|IC|均值<0.02→等权; 权重集中度>0.70→等权; 否则ic_weighted)
# A3: 等权兜底(样本<20→equal_weight)
# F2: synthesize_with_degradation(decide后分派到 multifactor_synthesis 三方法, 纯增量不替换既有方法)
# O1: SynthesisDecision + 合成信号 pd.Series
# [/ALGO_FLOW]
"""25号memo §3.7#1 合成降级链决策算法（SynthesisDegradationChain）。

降级链：回归优化 → IC 加权 → 等权兜底。决定"何时降级"的触发条件与降级路径，
与 §3.3 衰减监控联动（全池 |IC|<0.02 信号衰竭即降级等权）。

决策逻辑（decide）：
  ① 回归可行性（最高优先级）：forward_returns 观测≥120 且因子矩阵条件数<50 → regression；
     条件数≥50 → 降级 IC 加权。
  ② IC 加权（默认）：IC 样本≥20 时——全池 |IC| 均值<0.02 → 等权（信号衰竭）；
     单因子 IC 权重集中度>70% → 等权；否则 IC 加权。
  ③ IC 样本<20 → 等权兜底。

synthesize_with_degradation() 为统一入口：decide() 后分派到
multifactor_synthesis 的三个 production 方法，纯增量不替换现有方法。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import pandas as pd

from zephyr.factor.analysis.multifactor_synthesis import (
    synthesize_equal_weight,
    synthesize_ic_weighted,
    synthesize_regression,
)

log = logging.getLogger(__name__)

__all__ = [
    "DegradationChainParams",
    "SynthesisDecision",
    "decide",
    "synthesize_with_degradation",
]


@dataclass(frozen=True)
class DegradationChainParams:
    """降级链阈值参数（25号memo §3.7#1 参数表）。"""

    ic_min_samples: int = 20  # IC 样本<20→IC 加权不可靠→降级等权
    ic_weight_concentration: float = 0.70  # 单因子 IC 权重>70%→过度集中→降级等权
    ic_abs_floor: float = 0.02  # 全池 |IC|<0.02→信号衰竭→降级等权
    regression_min_obs: int = 120  # 前瞻收益观测<120→回归过拟合→降级 IC 加权
    condition_number_max: float = 50.0  # 因子矩阵条件数>50→共线性→降级 IC 加权


@dataclass(frozen=True)
class SynthesisDecision:
    """降级链决策结果。

    Attributes:
        method: 合成方法 "regression" / "ic_weighted" / "equal_weight"
        reason: 人类可读降级原因
        ic_weights: 归一化 IC 权重（ic_weighted 方法用；其他方法为空）
        degraded: 是否发生降级（非首选路径）
    """

    method: str
    reason: str
    ic_weights: dict[str, float] = field(default_factory=dict)
    degraded: bool = False


def _ic_stats(
    ic_history: dict[str, Sequence[float]],
) -> tuple[int, dict[str, float]]:
    """从历史 IC 序列计算 (样本数, 各因子 IC 均值)。

    样本数取各因子最小观测数（保守口径）；均值取各自序列均值。
    """
    means: dict[str, float] = {}
    n_samples = 0
    for fid, series in ic_history.items():
        vals = [float(v) for v in series if v is not None and not np.isnan(float(v))]
        if not vals:
            continue
        means[fid] = float(np.mean(vals))
        n_samples = len(vals) if n_samples == 0 else min(n_samples, len(vals))
    return n_samples, means


def _normalized_ic_weights(means: dict[str, float]) -> dict[str, float]:
    """IC 均值 → Σ|w|=1 归一化权重（与 synthesize_ic_weighted 同口径）。"""
    total = sum(abs(v) for v in means.values())
    if total < 1e-10:
        return {}
    return {k: v / total for k, v in means.items()}


def decide(
    factor_panel: dict[str, pd.Series],
    ic_history: dict[str, Sequence[float]],
    forward_returns: pd.Series | None = None,
    params: DegradationChainParams | None = None,
) -> SynthesisDecision:
    """合成降级链决策——regression → ic_weighted → equal_weight 三级降级。

    Args:
        factor_panel: factor_id → 因子值 Series（index 对齐）
        ic_history: factor_id → 历史 IC 观测序列（仅含决策日之前，INV-004）
        forward_returns: 已实现前向收益（回测中必须传 None 避免前瞻）
        params: 阈值参数

    Returns:
        SynthesisDecision。空面板直接等权兜底。
    """
    params = params or DegradationChainParams()
    if not factor_panel:
        return SynthesisDecision("equal_weight", "空因子面板→等权兜底", degraded=True)

    # ① 回归可行性（最高优先级）
    if forward_returns is not None:
        n_obs = int(forward_returns.dropna().shape[0])
        if n_obs >= params.regression_min_obs:
            panel = pd.DataFrame(factor_panel).fillna(0.0)
            cond = float(np.linalg.cond(panel.to_numpy())) if panel.shape[0] else np.inf
            if cond < params.condition_number_max:
                return SynthesisDecision(
                    "regression",
                    f"回归可行（观测 {n_obs}≥{params.regression_min_obs} 且条件数 {cond:.1f}<{params.condition_number_max:.0f}）",
                )
            return SynthesisDecision(
                "ic_weighted",
                f"条件数 {cond:.1f}≥{params.condition_number_max:.0f}（共线性）→降级 IC 加权",
                ic_weights=_normalized_ic_weights(_ic_stats(ic_history)[1]),
                degraded=True,
            )
        # 观测不足 120 → 继续走 IC 加权分支（不直接判回归）

    # ②③ IC 加权 / 等权兜底
    n_samples, means = _ic_stats(ic_history)
    if n_samples < params.ic_min_samples:
        return SynthesisDecision(
            "equal_weight",
            f"IC 样本 {n_samples}<{params.ic_min_samples}→IC 加权不可靠→等权兜底",
            degraded=True,
        )
    pool_abs_mean = float(np.mean([abs(v) for v in means.values()])) if means else 0.0
    if pool_abs_mean < params.ic_abs_floor:
        return SynthesisDecision(
            "equal_weight",
            f"全池 |IC| 均值 {pool_abs_mean:.4f}<{params.ic_abs_floor}（信号衰竭）→等权",
            degraded=True,
        )
    weights = _normalized_ic_weights(means)
    max_concentration = max((abs(w) for w in weights.values()), default=0.0)
    if max_concentration > params.ic_weight_concentration:
        return SynthesisDecision(
            "equal_weight",
            f"单因子 IC 权重 {max_concentration:.2%}>{params.ic_weight_concentration:.0%}（过度集中）→等权",
            degraded=True,
        )
    return SynthesisDecision("ic_weighted", "IC 加权（默认路径）", ic_weights=weights)


def synthesize_with_degradation(
    factor_values: dict[str, pd.Series],
    ic_history: dict[str, Sequence[float]] | None = None,
    forward_returns: pd.Series | None = None,
    params: DegradationChainParams | None = None,
) -> tuple[pd.Series, SynthesisDecision]:
    """合成统一入口——decide() 后分派到 3 个 production 合成方法。

    Returns:
        (合成信号 pd.Series, SynthesisDecision)
    """
    decision = decide(factor_values, ic_history or {}, forward_returns, params)
    if decision.method == "regression" and forward_returns is not None:
        return synthesize_regression(factor_values, forward_returns), decision
    if decision.method == "ic_weighted" and decision.ic_weights:
        return synthesize_ic_weighted(factor_values, decision.ic_weights), decision
    if decision.method != "equal_weight":
        # ic_weighted 但无有效权重 → 等权兜底
        log.warning("degradation_chain: %s 无有效权重，退化为等权", decision.method)
    return synthesize_equal_weight(factor_values), decision
