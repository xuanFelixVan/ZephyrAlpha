# [BLUEPRINT] 90_methodology_open_questions.md §5（v2.0.0 裁定）
# [MODULE] zephyr.ex_sor.services.t0_cost_model
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] 无（纯 Decimal 计算）
# [CONSUMERS] 做T策略开仓前置检查（接线待排期，本批仅交付模块本体）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 佣金=max(费率×成交额,最低5元)；印花税仅卖出边；滑点按双边计；失败风险溢价=隔夜底仓暴露×隔夜VaR
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非正成交额→ValueError
# [TESTS] tests/ex_sor/test_t0_cost_model.py
# [A_module] module_id=MOD-XS-T0COST | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_EX_SOR — 做T成本模型（90 号 Phase1 项①，注册表条目 CST-T0-001）

裁定真源：90_methodology_open_questions.md §5（v2.0.0 简化采纳）：
  - 做T额外成本 = 滑点×2（一买一卖两次滑点）+ 失败风险溢价；
  - 单次往返硬成本≈0.10-0.15%（双边佣金+卖出印花税+双倍滑点），
    预期价差≥0.3% 才有正期望——做T开仓硬性前置条件（与 §21 regime 过滤联动）；
  - 最低 5 元佣金显式建模（单笔 <5 万元时实际费率被抬升至万5以上，
    是小资金+做T高频最大隐性成本）；
  - 印花税=卖出单边 0.05%（万5，2023-08-28 减半后现行）；
  - 滑点按策略分档：高流动票 0.05-0.1%，打板/事件票 0.15-0.3%（乘成交概率折减）。

失败风险溢价（§5/§8）：日内未接回底仓的隔夜风险 = 隔夜底仓暴露 × 隔夜 VaR。

注意：本模块为 90 号 Phase1 交付物，MATURITY=testing；生产链路（做T策略开仓
前置检查/回测成本注入点）接线挂起待 Owner（宪章 B-007 纪律）。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

__all__ = [
    "SlippageTier",
    "T0CostConfig",
    "T0CostBreakdown",
    "T0_MIN_EDGE_RATE",
    "calc_t0_roundtrip_cost",
    "t0_open_allowed",
]

#: 做T开仓硬前置：预期价差 ≥0.3% 才有正期望（90 号 §5 裁定）
T0_MIN_EDGE_RATE: Decimal = Decimal("0.003")


class SlippageTier(str, Enum):
    """策略分档滑点（90 号 §5 裁定②）。"""

    HIGH_LIQUIDITY = "high_liquidity"  # 高流动票 0.05-0.1%/边（默认取上限 10bps）
    DABAN_EVENT = "daban_event"  # 打板/事件票 0.15-0.3%/边（默认取中值 20bps）


#: 分档默认滑点（bps/边）；打板档可再乘成交概率折减（封板买不进概率，条件成交修正）
_TIER_SLIPPAGE_BPS: dict[SlippageTier, Decimal] = {
    SlippageTier.HIGH_LIQUIDITY: Decimal("10"),
    SlippageTier.DABAN_EVENT: Decimal("20"),
}


@dataclass(frozen=True)
class T0CostConfig:
    """做T成本配置（费率按账户配置不硬编码——默认值对齐 CST-ASTOCK-001）。"""

    commission_rate: Decimal = Decimal("0.0000854")  # 佣金万0.854（双边；2026-08-21 费率口径统一 #233，与主口径对齐 Owner 实盘协议费率）
    min_commission: Decimal = Decimal("5")  # 最低佣金 5 元/笔（显式建模）
    stamp_duty_rate: Decimal = Decimal("0.0005")  # 印花税万5（卖出单边）
    slippage_tier: SlippageTier = SlippageTier.HIGH_LIQUIDITY
    fill_probability: Decimal = Decimal("1.0")  # 打板成交概率折减（<1 时滑点按条件成交修正）


@dataclass(frozen=True)
class T0CostBreakdown:
    """单次做T往返成本分解（元）。"""

    commission_total: Decimal  # 双边佣金合计（含最低佣金抬升）
    stamp_duty: Decimal  # 卖出边印花税
    slippage_total: Decimal  # 双边滑点合计
    failure_risk_premium: Decimal  # 失败风险溢价（隔夜暴露×隔夜VaR）
    total: Decimal  # 总成本


def _commission(notional: Decimal, cfg: T0CostConfig) -> Decimal:
    c = notional * cfg.commission_rate
    return c if c >= cfg.min_commission else cfg.min_commission


def calc_t0_roundtrip_cost(
    buy_notional: Decimal,
    sell_notional: Decimal,
    config: T0CostConfig | None = None,
    overnight_exposure: Decimal = Decimal("0"),
    overnight_var_rate: Decimal = Decimal("0"),
) -> T0CostBreakdown:
    """计算单次做T往返总成本（元）。

    Args:
        buy_notional: 买入成交额（元）
        sell_notional: 卖出成交额（元）
        config: 成本配置（None=默认 CST-ASTOCK-001 对齐值）
        overnight_exposure: 失败情形隔夜底仓暴露（元，0=全额接回无溢价）
        overnight_var_rate: 隔夜 VaR 比率（如 0.02=2%）

    Returns:
        T0CostBreakdown 成本分解
    """
    if buy_notional <= 0 or sell_notional <= 0:
        raise ValueError("买卖成交额必须为正")
    if overnight_exposure < 0 or overnight_var_rate < 0:
        raise ValueError("隔夜暴露/VaR 不能为负")
    cfg = config or T0CostConfig()

    commission_total = _commission(buy_notional, cfg) + _commission(sell_notional, cfg)
    stamp_duty = sell_notional * cfg.stamp_duty_rate

    slip_bps = _TIER_SLIPPAGE_BPS[cfg.slippage_tier] * cfg.fill_probability
    slippage_total = (buy_notional + sell_notional) * slip_bps / Decimal("10000")

    failure_risk_premium = overnight_exposure * overnight_var_rate

    total = commission_total + stamp_duty + slippage_total + failure_risk_premium
    return T0CostBreakdown(
        commission_total=commission_total,
        stamp_duty=stamp_duty,
        slippage_total=slippage_total,
        failure_risk_premium=failure_risk_premium,
        total=total,
    )


def t0_open_allowed(expected_edge_rate: Decimal) -> bool:
    """做T开仓硬前置：预期价差率 ≥0.3%（90 号 §5/§21 裁定）。"""
    return expected_edge_rate >= T0_MIN_EDGE_RATE
