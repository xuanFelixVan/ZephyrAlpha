# [BLUEPRINT] MOD-SIM-027 | docs/03_modules/_domain_simulation/blueprint.md
# [MODULE] zephyr.simulation.volume_aware_impact
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES]
# [CONSUMERS] 预留(portfolio-rebalance级撮合升级时评估采纳, 53号§3.2 v2.0候选)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 单调性(|Δw|增→impact增);dollar_volume<=0→impact=0不崩;买卖对称(abs);impact_coef=0→impact=0向后兼容legacy flat
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VolumeAwareImpactError(ZA-SIM-0027)
# [TESTS] tests/simulation/test_volume_aware_impact.py
# [TTL] permanent
# [A_module] module_id=MOD-SIM-027 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [ALGO_FLOW]
# I1: delta_weight(权重变化) + notional(组合名义金额) + dollar_volume(标的成交额) + impact_coef
# A1: volume_aware_sqrt_impact(impact=coef×√(|Δw|×notional/dollar_volume), 零量fallback/符号对称/零系数兼容)
# A2: volume_aware_sqrt_impact_batch(逐标的批量形式, NAV loop rebalance_cost 用)
# O1: impact 成本率(标量或list[float], 占notional比例)
# [/ALGO_FLOW]
"""citrusquant volume-aware sqrt impact 形式模块(53号 §3.2 v2.0 候选)

职责:
  - citrusquant #19(2026-07-10 合并)的 square-root impact 工程实现形式——
    按权重变化率而非订单大小建模, 直接在 NAV loop 的 rebalance_cost 中用
    participation-scaled sqrt impact 替换 flat slippage:
        impact[c] = impact_coef × sqrt(|Δw[c]| × notional / dollar_volume[c])
  - 与既有 SquareRootImpactPredictor 同源(sqrt market impact): 既有实现用
    order_size/ADV 参与率(order-driven 单笔场景), 本模块用 |Δw|×notional/dollar_volume
    权重变化率(rebalance-driven 组合再平衡场景)

验收标准(citrusquant PR 四条, 53号 §3.2 采纳为通用工程验收):
  ① 单调性: |Δw| 增大 → impact 增大
  ② NaN/zero volume fallback: dollar_volume<=0 时 impact=0(不崩)
  ③ sign symmetry: 买卖对称(abs 处理)
  ④ impact_coef=0 时逐位复现 legacy flat slippage 行为(impact 恒 0, 向后兼容)

约束:
  - 函数级候选, 不改动既有 slippage_analyzer(MVP 仍用 SquareRootImpactPredictor)
  - 纯函数无副作用, 输入注入式

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/53_simulation_live_path.md §3.2
"""

from __future__ import annotations

import math

__all__ = [
    "VolumeAwareImpactError",
    "volume_aware_sqrt_impact",
    "volume_aware_sqrt_impact_batch",
]


class VolumeAwareImpactError(Exception):
    """volume-aware impact 计算错误(输入非法)"""

    error_code = "ZA-SIM-0027"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


def _validate_common(notional: float, impact_coef: float) -> tuple[float, float]:
    try:
        notional_f = float(notional)
        coef_f = float(impact_coef)
    except (TypeError, ValueError) as exc:
        raise VolumeAwareImpactError(
            f"notional/impact_coef必须是数值: {notional!r}, {impact_coef!r}"
        ) from exc
    if notional_f < 0:
        raise VolumeAwareImpactError(f"notional必须>=0, got {notional_f}")
    if coef_f < 0:
        raise VolumeAwareImpactError(f"impact_coef必须>=0, got {coef_f}")
    return notional_f, coef_f


def volume_aware_sqrt_impact(
    delta_weight: float,
    notional: float,
    dollar_volume: float,
    impact_coef: float,
) -> float:
    """citrusquant 形式单标的 sqrt impact 成本率

    impact = impact_coef × sqrt(|Δw| × notional / dollar_volume)

    Args:
        delta_weight: 权重变化(带符号, 内部 abs 实现买卖对称)
        notional: 组合名义金额(>=0)
        dollar_volume: 标的成交额(<=0 时 fallback 返回 0.0, 不崩)
        impact_coef: 冲击系数(=0 时恒返回 0.0, 向后兼容 legacy flat slippage)

    Returns:
        float: impact 成本率(占 notional 比例, >=0)

    Raises:
        VolumeAwareImpactError: delta_weight 非有限数值 / notional / impact_coef 非法
    """
    notional_f, coef_f = _validate_common(notional, impact_coef)
    try:
        dw_f = float(delta_weight)
    except (TypeError, ValueError) as exc:
        raise VolumeAwareImpactError(f"delta_weight必须是数值: {delta_weight!r}") from exc
    if not math.isfinite(dw_f):
        raise VolumeAwareImpactError(f"delta_weight必须有限, got {dw_f}")

    # 验收④: impact_coef=0 → 恒 0(legacy flat 兼容位, 调用方叠加 flat 部分)
    if coef_f == 0.0:
        return 0.0
    # 验收②: zero/NaN volume fallback(不崩)
    try:
        dv_f = float(dollar_volume)
    except (TypeError, ValueError) as exc:
        raise VolumeAwareImpactError(f"dollar_volume必须是数值: {dollar_volume!r}") from exc
    if not math.isfinite(dv_f) or dv_f <= 0:
        return 0.0
    # 验收③: sign symmetry(abs)
    participation = abs(dw_f) * notional_f / dv_f
    return coef_f * math.sqrt(participation)


def volume_aware_sqrt_impact_batch(
    delta_weights: list[float],
    notional: float,
    dollar_volumes: list[float],
    impact_coef: float,
) -> list[float]:
    """citrusquant 形式批量 impact(NAV loop rebalance_cost 用)

    Args:
        delta_weights: 各标的权重变化列表
        notional: 组合名义金额(>=0)
        dollar_volumes: 各标的成交额列表(长度须与 delta_weights 一致)
        impact_coef: 冲击系数

    Returns:
        list[float]: 各标的 impact 成本率

    Raises:
        VolumeAwareImpactError: 长度不一致或输入非法
    """
    if len(delta_weights) != len(dollar_volumes):
        raise VolumeAwareImpactError(
            f"delta_weights与dollar_volumes长度必须一致, got {len(delta_weights)} vs {len(dollar_volumes)}"
        )
    return [
        volume_aware_sqrt_impact(dw, notional, dv, impact_coef)
        for dw, dv in zip(delta_weights, dollar_volumes)
    ]
