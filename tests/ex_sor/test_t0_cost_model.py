# [BLUEPRINT] MOD-EX_SOR_EXT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_test_t0_cost_model | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ex_sor.test_t0_cost_model
# [TESTS] src/zephyr/ex_sor/services/t0_cost_model.py
# [TTL] task_bound
"""90 号 Phase1 项①：做T成本模型（CST-T0-001）已知答案 toy 断言。

裁定真源：90_methodology_open_questions.md §5（v2.0.0）——
  做T额外成本=滑点×2+失败风险溢价（隔夜底仓暴露×隔夜VaR）；
  最低 5 元佣金必须显式建模；印花税率卖出单边万5；
  预期价差≥0.3% 才有正期望（开仓硬前置）。
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from zephyr.ex_sor.services.t0_cost_model import (
    T0_MIN_EDGE_RATE,
    SlippageTier,
    T0CostConfig,
    calc_t0_roundtrip_cost,
    t0_open_allowed,
)


class TestDefaults:
    """默认配置对齐主口径（2026-08-21 #233：佣金万0.854/最低5元/印花税万5）。"""

    def test_default_rates(self):
        cfg = T0CostConfig()
        assert cfg.commission_rate == Decimal("0.0000854")
        assert cfg.min_commission == Decimal("5")
        assert cfg.stamp_duty_rate == Decimal("0.0005")

    def test_min_edge_is_03pct(self):
        """90 号 §5：单次往返硬成本≈0.10-0.15%，预期价差≥0.3% 才有正期望。"""
        assert T0_MIN_EDGE_RATE == Decimal("0.003")


class TestRoundTripCost:
    def test_small_notional_min_commission_kicks_in(self):
        """1 万元双边：佣金被最低 5 元抬升（费率仅 0.854 元 < 5 元）。

        佣金 5+5=10，印花税 10000×0.0005=5，
        高流动档滑点 10bps/边 × 双边 = 20000×0.001=20 → 合计 35 元。
        （2026-08-21 #233：费率降至万0.854 后本场景仍全触最低佣金，金额不变）
        """
        cfg = T0CostConfig(slippage_tier=SlippageTier.HIGH_LIQUIDITY)
        cost = calc_t0_roundtrip_cost(buy_notional=Decimal("10000"), sell_notional=Decimal("10000"), config=cfg)
        assert cost.commission_total == Decimal("10")
        assert cost.stamp_duty == Decimal("5")
        assert cost.slippage_total == Decimal("20")
        assert cost.total == Decimal("35")

    def test_large_notional_rate_applies(self):
        """10 万元双边：佣金 8.54+8.54=17.08（#233 万0.854），印花税 50，滑点 200 → 267.08。"""
        cfg = T0CostConfig(slippage_tier=SlippageTier.HIGH_LIQUIDITY)
        cost = calc_t0_roundtrip_cost(buy_notional=Decimal("100000"), sell_notional=Decimal("100000"), config=cfg)
        assert cost.commission_total == Decimal("17.08")
        assert cost.stamp_duty == Decimal("50")
        assert cost.slippage_total == Decimal("200")
        assert cost.total == Decimal("267.08")

    def test_daban_tier_slippage_higher(self):
        """打板/事件档滑点（默认 20bps/边）高于高流动档（10bps/边）。"""
        cfg = T0CostConfig(slippage_tier=SlippageTier.DABAN_EVENT)
        cost = calc_t0_roundtrip_cost(buy_notional=Decimal("100000"), sell_notional=Decimal("100000"), config=cfg)
        assert cost.slippage_total == Decimal("400")

    def test_failure_risk_premium(self):
        """失败风险溢价=隔夜底仓暴露×隔夜VaR（90 号 §5）。"""
        cfg = T0CostConfig(slippage_tier=SlippageTier.HIGH_LIQUIDITY)
        cost = calc_t0_roundtrip_cost(
            buy_notional=Decimal("10000"),
            sell_notional=Decimal("10000"),
            config=cfg,
            overnight_exposure=Decimal("50000"),
            overnight_var_rate=Decimal("0.02"),
        )
        assert cost.failure_risk_premium == Decimal("1000")
        assert cost.total == Decimal("35") + Decimal("1000")

    def test_zero_exposure_no_premium(self):
        cfg = T0CostConfig()
        cost = calc_t0_roundtrip_cost(buy_notional=Decimal("10000"), sell_notional=Decimal("10000"), config=cfg)
        assert cost.failure_risk_premium == Decimal("0")


class TestOpenPrecondition:
    def test_edge_below_03pct_rejected(self):
        assert t0_open_allowed(expected_edge_rate=Decimal("0.002")) is False

    def test_edge_at_03pct_allowed(self):
        assert t0_open_allowed(expected_edge_rate=Decimal("0.003")) is True

    def test_invalid_notional_raises(self):
        with pytest.raises(ValueError):
            calc_t0_roundtrip_cost(buy_notional=Decimal("0"), sell_notional=Decimal("10000"), config=T0CostConfig())
