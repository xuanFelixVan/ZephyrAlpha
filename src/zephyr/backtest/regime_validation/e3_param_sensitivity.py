# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §4.4 D 类 / §4.5 E3 / §5
# [MODULE] zephyr.backtest.regime_validation.e3_param_sensitivity
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan Phase 4 E3
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 只消费既有网格回测产出的效果指标, 不重跑回测; 相对变化=|扰动效果−基线|/|基线|; 基线≈0 时相对变化退化定义(见代码); frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] E3SensitivityError(ZA-BT-0028)
# [TESTS] tests/backtest/test_e3_param_sensitivity.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: baseline_effect(基线参数下的效果指标, 如 MaxDD 改善幅度)
# I2: points(各参数 ±20% 扰动后的效果指标, 既有网格回测产物)
# I3: tolerance=0.30(§4.4: ±20% 扰动效果变化<30% → 稳健)
# A1: analyze_param_sensitivity(按参数聚合→相对变化→悬崖检测)
# A2: perturb_pm20(基线值×0.8/×1.2 扰动值生成器)
# O1: E3SensitivityReport(逐参数判定 + max_rel_change + passed + 悬崖参数清单)
# [/ALGO_FLOW]
"""D_BACKTEST — E3 参数敏感性 ±20% 网格分析（11 号 memo §4.5 E3 / §4.4）。

纯分析函数：不重跑回测，只消费既有 ±20% 扰动网格回测产出的效果指标
（如 MaxDD 改善幅度），按 §5 E3 门槛「±20% 扰动效果变化 < 30%」判定稳健性，
并识别「最优参数孤岛」（悬崖参数 = 邻域效果骤降，过拟合警告）。

依据: 11_regime_backtest_validation_plan §4.4 / §4.5 E3 / §5
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

_EPS = 1e-12


class E3SensitivityError(ZephyrBaseError):
    """ZA-BT-0028: E3 参数敏感性分析错误（输入非法）。"""

    error_code = "ZA-BT-0028"


@dataclass(frozen=True)
class E3PerturbationPoint:
    """单参数单方向扰动后的效果——不可变。"""

    name: str  # 参数名
    factor: float  # 扰动倍率（0.8=−20% / 1.2=+20%）
    effect: float  # 扰动后的效果指标（如 MaxDD 改善幅度）


@dataclass(frozen=True)
class E3ParamVerdict:
    """单参数敏感性判定——不可变。"""

    name: str
    worst_effect: float  # 扰动后最差效果
    max_rel_change: float  # 最大相对变化 |effect−baseline|/|baseline|
    robust: bool  # max_rel_change < tolerance


@dataclass(frozen=True)
class E3SensitivityReport:
    """E3 参数敏感性报告——不可变。"""

    baseline_effect: float
    verdicts: tuple[E3ParamVerdict, ...]
    max_rel_change: float  # 全参数最大相对变化
    passed: bool  # 无悬崖参数（全部 < tolerance）
    cliff_params: tuple[str, ...]  # 悬崖参数（≥tolerance，过拟合警告）
    summary: str


def perturb_pm20(base_value: float) -> tuple[float, float]:
    """±20% 扰动值生成器：返回 (×0.8, ×1.2)。"""
    return (base_value * 0.8, base_value * 1.2)


def _rel_change(effect: float, baseline: float) -> float:
    """相对变化 |effect−baseline|/|baseline|；基线≈0 时：扰动也≈0 → 0，否则 → inf。"""
    diff = abs(effect - baseline)
    if abs(baseline) < _EPS:
        return 0.0 if diff < _EPS else float("inf")
    return diff / abs(baseline)


def analyze_param_sensitivity(
    baseline_effect: float,
    points: list[E3PerturbationPoint],
    tolerance: float = 0.30,
) -> E3SensitivityReport:
    """E3 主入口：±20% 扰动网格的稳健性判定。

    Args:
        baseline_effect: 基线参数下的效果指标（如 MaxDD 改善幅度）。
        points: 各参数 ±20% 扰动后的效果（既有网格回测产物），每参数可多点。
        tolerance: 相对变化门槛（§4.4/§5 E3=0.30，<30% 为稳健）。

    Returns:
        E3SensitivityReport；passed=False 时 cliff_params 为过拟合警告清单。

    Raises:
        E3SensitivityError: points 为空 / tolerance 非正 / 效果值非有限。
    """
    if not points:
        raise E3SensitivityError("points 不能为空")
    if tolerance <= 0:
        raise E3SensitivityError(f"tolerance 需 >0: {tolerance}")
    if abs(baseline_effect) == float("inf") or baseline_effect != baseline_effect:
        raise E3SensitivityError(f"baseline_effect 非有限: {baseline_effect}")
    for p in points:
        if p.effect != p.effect or abs(p.effect) == float("inf"):
            raise E3SensitivityError(f"参数 {p.name} 的 effect 非有限: {p.effect}")

    by_name: dict[str, list[float]] = {}
    for p in points:
        by_name.setdefault(p.name, []).append(p.effect)

    verdicts: list[E3ParamVerdict] = []
    for name in sorted(by_name):
        effects = by_name[name]
        max_rel = max(_rel_change(e, baseline_effect) for e in effects)
        verdicts.append(
            E3ParamVerdict(
                name=name,
                worst_effect=min(effects),
                max_rel_change=max_rel,
                robust=max_rel < tolerance,
            )
        )

    cliffs = tuple(v.name for v in verdicts if not v.robust)
    max_rel_change = max(v.max_rel_change for v in verdicts)
    passed = not cliffs
    summary = (
        f"E3 参数敏感性: {len(verdicts)} 参数 ±20% 扰动, 基线效果={baseline_effect:+.4f}, "
        f"最大相对变化={max_rel_change:.2%} 门槛<{tolerance:.0%} → "
        f"{'稳健' if passed else f'悬崖参数={list(cliffs)}（过拟合警告）'}"
    )
    _logger.info("E3 完成: %s", summary)
    return E3SensitivityReport(
        baseline_effect=baseline_effect,
        verdicts=tuple(verdicts),
        max_rel_change=max_rel_change,
        passed=passed,
        cliff_params=cliffs,
        summary=summary,
    )


__all__ = [
    "E3ParamVerdict",
    "E3PerturbationPoint",
    "E3SensitivityError",
    "E3SensitivityReport",
    "analyze_param_sensitivity",
    "perturb_pm20",
]
