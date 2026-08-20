# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §0.5.7 D3 / §4.4
# [MODULE] zephyr.regime.validation.d3_aggregation_perturbation
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan Phase 3 D3
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 聚合公式重放镜像 regime_detector._compute_risk_signal(含#1门控/min聚合/clamp[0.30,1.00]); 只扰动共振惩罚步长0.05与机会恢复上限0.25两参数; 效果代理指标=RiskSignal序列均值; 只读输入
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] D3AggregationError(ZA-REGIME-0036)
# [TESTS] tests/regime/validation/test_d3_aggregation_perturbation.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: risk_inputs_series(逐日 risk_signal_inputs: {"params":{#id:coef}, "opportunity":{...}}, 既有 detector 产物)
# I2: 扰动幅度 pct=0.20 + tolerance=0.30(§4.4 D 类门槛)
# F1: aggregate_risk_signal(RiskBase×共振惩罚+机会恢复→clamp, 参数化的生产公式镜像)
# A1: run_d3_perturbation(两参数各 ×{0.8,1.2} 四点扰动→重放序列→均值相对变化判定)
# O1: D3PerturbationReport(基线均值 + 逐扰动点统计 + max_rel_change + passed)
# [/ALGO_FLOW]
"""D_REGIME — D3 聚合公式参数扰动分析（11 号 memo §0.5.7 D3）。

纯分析函数：不重跑回测，只把既有逐日 risk_inputs 产物在参数扰动后的聚合
公式下重放。扰动对象 = 10_regime_detector_spec §5.3.3 聚合公式的两个常数：
共振惩罚步长 0.05（每多一个异常参数再扣 5%，下限 ×0.80）与机会恢复上限
+0.25（#11 鬼故事 + #13 利空不跌）。按 §4.4 D 类门槛（±20% 扰动效果变化
<30%）判定稳健性。

aggregate_risk_signal 是 regime_detector._compute_risk_signal 的参数化镜像
（含 #1 门控、min 聚合、clamp[0.30,1.00]），生产常数为默认值。

依据: 11_regime_backtest_validation_plan §0.5.7 D3 / §4.4; 10_regime_detector_spec §5.3.3
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

_EPS = 1e-12

# 生产常数（10_regime_detector_spec §5.3.3 / regime_detector._compute_risk_signal）
DEFAULT_RESONANCE_STEP = 0.05  # 共振惩罚步长
DEFAULT_RESONANCE_FLOOR = 0.80  # 共振惩罚下限
DEFAULT_RECOVERY_CAP = 0.25  # 机会恢复上限
_RISK_PARAM_IDS = tuple(list(range(1, 11)) + [12])  # #1-#10/#12（#11/#13 走机会恢复）


class D3AggregationError(ZephyrBaseError):
    """ZA-REGIME-0036: D3 聚合扰动分析错误（输入非法）。"""

    error_code = "ZA-REGIME-0036"


@dataclass(frozen=True)
class D3PerturbationPoint:
    """单参数单方向扰动结果——不可变。"""

    param: str  # resonance_step / recovery_cap
    factor: float  # 0.8 / 1.2
    perturbed_value: float
    mean_risk: float  # 重放 RiskSignal 序列均值
    share_contracted: float  # RiskSignal<1.0 天数占比
    rel_change: float  # 均值相对基线变化


@dataclass(frozen=True)
class D3PerturbationReport:
    """D3 聚合扰动报告——不可变。"""

    baseline_mean: float
    points: tuple[D3PerturbationPoint, ...]
    max_rel_change: float
    passed: bool  # max_rel_change < tolerance
    summary: str


def aggregate_risk_signal(
    params: dict[int, float],
    opportunity: dict[str, float] | None = None,
    resonance_step: float = DEFAULT_RESONANCE_STEP,
    resonance_floor: float = DEFAULT_RESONANCE_FLOOR,
    recovery_cap: float = DEFAULT_RECOVERY_CAP,
    lower: float = 0.30,
    upper: float = 1.00,
) -> float:
    """RiskSignal 聚合公式（regime_detector._compute_risk_signal 参数化镜像）。

    RiskSignal = clamp[lower, RiskBase × 共振惩罚 + 机会恢复, upper]
      RiskBase = min(#1-#10/#12 系数)（#1 门控：#1≥1.0 时直接返回 1.0）
      共振惩罚 = max(floor, 1 − step × max(0, 异常参数数−1))
      机会恢复 = min(news_ghost + bad_news_flat, cap)
    """
    if not params:
        return 1.0
    primary = float(params.get(1, 1.0))
    if primary >= 1.0:
        return 1.0
    coefs = [float(params[i]) for i in _RISK_PARAM_IDS if i in params and params[i] is not None]
    if not coefs:
        return 1.0
    risk_base = min(coefs)
    anomaly_count = sum(1 for c in coefs if c < 1.0)
    resonance = max(resonance_floor, 1.0 - resonance_step * max(0, anomaly_count - 1))
    recovery = 0.0
    if isinstance(opportunity, dict):
        recovery = float(opportunity.get("news_ghost", 0.0)) + float(opportunity.get("bad_news_flat", 0.0))
    recovery = min(recovery, recovery_cap)
    return max(lower, min(upper, risk_base * resonance + recovery))


def run_d3_perturbation(
    risk_inputs_series: Sequence[dict[str, Any]],
    pct: float = 0.20,
    tolerance: float = 0.30,
) -> D3PerturbationReport:
    """D3 主入口：共振惩罚 0.05 / 机会恢复 0.25 两参数 ±20% 扰动分析。

    Args:
        risk_inputs_series: 逐日 risk_signal_inputs 序列（{"params"/"opportunity"}），
            空 dict 项按生产降级逻辑得 RiskSignal=1.0。
        pct: 扰动幅度（默认 ±20%）。
        tolerance: 相对变化门槛（§4.4 D 类=0.30）。

    Raises:
        D3AggregationError: 空序列 / pct 或 tolerance 非正。
    """
    if pct <= 0 or tolerance <= 0:
        raise D3AggregationError(f"pct/tolerance 需 >0: {pct}/{tolerance}")
    if not risk_inputs_series:
        raise D3AggregationError("risk_inputs_series 不能为空")

    def _series(resonance_step: float, recovery_cap: float) -> np.ndarray:
        vals = np.empty(len(risk_inputs_series), dtype=float)
        for i, item in enumerate(risk_inputs_series):
            item = item or {}
            vals[i] = aggregate_risk_signal(
                item.get("params") or {},
                item.get("opportunity"),
                resonance_step=resonance_step,
                recovery_cap=recovery_cap,
            )
        return vals

    baseline = _series(DEFAULT_RESONANCE_STEP, DEFAULT_RECOVERY_CAP)
    baseline_mean = float(baseline.mean())

    points: list[D3PerturbationPoint] = []
    for param, base_value in (
        ("resonance_step", DEFAULT_RESONANCE_STEP),
        ("recovery_cap", DEFAULT_RECOVERY_CAP),
    ):
        for factor in (1.0 - pct, 1.0 + pct):
            new_value = base_value * factor
            series = _series(
                new_value if param == "resonance_step" else DEFAULT_RESONANCE_STEP,
                new_value if param == "recovery_cap" else DEFAULT_RECOVERY_CAP,
            )
            mean_risk = float(series.mean())
            rel = abs(mean_risk - baseline_mean) / max(abs(baseline_mean), _EPS)
            points.append(
                D3PerturbationPoint(
                    param=param,
                    factor=factor,
                    perturbed_value=new_value,
                    mean_risk=mean_risk,
                    share_contracted=float(np.mean(series < 1.0)),
                    rel_change=rel,
                )
            )

    max_rel = max(p.rel_change for p in points)
    passed = max_rel < tolerance
    summary = (
        f"D3 聚合公式 ±{pct:.0%} 扰动: 基线均值={baseline_mean:.4f}, "
        f"最大相对变化={max_rel:.2%} 门槛<{tolerance:.0%} → "
        f"{'稳健' if passed else '敏感（聚合常数悬崖）'}"
    )
    _logger.info("D3 完成: %s", summary)
    return D3PerturbationReport(
        baseline_mean=baseline_mean,
        points=tuple(points),
        max_rel_change=max_rel,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "DEFAULT_RECOVERY_CAP",
    "DEFAULT_RESONANCE_FLOOR",
    "DEFAULT_RESONANCE_STEP",
    "D3AggregationError",
    "D3PerturbationPoint",
    "D3PerturbationReport",
    "aggregate_risk_signal",
    "run_d3_perturbation",
]
