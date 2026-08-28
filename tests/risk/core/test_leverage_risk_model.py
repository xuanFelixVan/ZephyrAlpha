# [A_test] module_id: CAND-CRYPTO-008 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 94_crypto_quant_expansion | §4.4
# [MODULE] tests.risk.core.test_leverage_risk_model
# [INVARIANTS] 爆仓价多/空公式;维持保证金率阶梯取档(边界含上限);资金费率成本多付空收;margin_ratio>=1爆仓;distance正值=安全;非法输入抛InvalidLeverageRiskInputError
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/core/test_leverage_risk_model.py
# [TTL] task_bound
"""杠杆风控模型测试（CAND-CRYPTO-008，94 号 §4.4：爆仓价/维持保证金/资金费率）。"""

from __future__ import annotations

import math

import pytest

from zephyr.risk.core.leverage_risk_model import (
    DEFAULT_MAINTENANCE_MARGIN_TIERS,
    InvalidLeverageRiskInputError,
    MaintenanceMarginTier,
    PositionSide,
    assess_leverage_position,
    calculate_distance_to_liquidation,
    calculate_funding_cost,
    calculate_liquidation_price,
    calculate_margin_ratio,
    get_maintenance_margin_rate,
)


class TestLiquidationPrice:
    def test_long_formula(self):
        """多头爆仓价 = entry * (1 - 1/leverage + mmr)。"""
        liq = calculate_liquidation_price(10_000.0, 10.0, 0.004, PositionSide.LONG)
        assert liq == pytest.approx(9_040.0)

    def test_long_default_side(self):
        liq = calculate_liquidation_price(10_000.0, 10.0, 0.004)
        assert liq == pytest.approx(9_040.0)

    def test_short_formula(self):
        """空头爆仓价 = entry * (1 + 1/leverage - mmr)。"""
        liq = calculate_liquidation_price(10_000.0, 10.0, 0.004, PositionSide.SHORT)
        assert liq == pytest.approx(10_960.0)

    def test_leverage_1_long(self):
        """1x 多头：爆仓价 = entry * mmr（亏光初始保证金即爆）。"""
        liq = calculate_liquidation_price(10_000.0, 1.0, 0.004, PositionSide.LONG)
        assert liq == pytest.approx(40.0)

    def test_leverage_1_short(self):
        liq = calculate_liquidation_price(10_000.0, 1.0, 0.004, PositionSide.SHORT)
        assert liq == pytest.approx(19_960.0)

    def test_higher_leverage_closer_to_entry(self):
        """杠杆越高爆仓价越贴近开仓价。"""
        liq_5x = calculate_liquidation_price(10_000.0, 5.0, 0.004)
        liq_20x = calculate_liquidation_price(10_000.0, 20.0, 0.004)
        assert 10_000.0 - liq_20x < 10_000.0 - liq_5x

    def test_invalid_entry_price(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_liquidation_price(0.0, 10.0, 0.004)

    def test_invalid_leverage(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_liquidation_price(10_000.0, 0.5, 0.004)

    def test_invalid_mmr(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_liquidation_price(10_000.0, 10.0, 1.0)


class TestMaintenanceMarginRate:
    def test_first_tier(self):
        assert get_maintenance_margin_rate(30_000.0) == pytest.approx(0.004)

    def test_tier_cap_boundary_inclusive(self):
        """名义价值等于档位上限 → 落本档。"""
        assert get_maintenance_margin_rate(50_000.0) == pytest.approx(0.004)
        assert get_maintenance_margin_rate(50_001.0) == pytest.approx(0.005)

    def test_all_tiers(self):
        assert get_maintenance_margin_rate(250_000.0) == pytest.approx(0.005)
        assert get_maintenance_margin_rate(1_000_000.0) == pytest.approx(0.01)
        assert get_maintenance_margin_rate(10_000_000.0) == pytest.approx(0.025)
        assert get_maintenance_margin_rate(100_000_000.0) == pytest.approx(0.05)

    def test_rate_monotonic_with_notional(self):
        """档位随名义价值单调不降（交易所规则）。"""
        rates = [
            get_maintenance_margin_rate(n)
            for n in (10_000.0, 100_000.0, 500_000.0, 5_000_000.0, 50_000_000.0)
        ]
        assert rates == sorted(rates)

    def test_custom_tiers(self):
        tiers = (
            MaintenanceMarginTier(1_000.0, 0.01),
            MaintenanceMarginTier(math.inf, 0.02),
        )
        assert get_maintenance_margin_rate(500.0, tiers) == pytest.approx(0.01)
        assert get_maintenance_margin_rate(5_000.0, tiers) == pytest.approx(0.02)

    def test_invalid_notional(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            get_maintenance_margin_rate(0.0)

    def test_empty_tiers(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            get_maintenance_margin_rate(1_000.0, ())

    def test_invalid_tier_rate(self):
        tiers = (MaintenanceMarginTier(math.inf, 1.5),)
        with pytest.raises(InvalidLeverageRiskInputError):
            get_maintenance_margin_rate(1_000.0, tiers)


class TestFundingCost:
    def test_long_pays_positive_rate(self):
        """正费率多头付：cost = notional * rate * periods。"""
        cost = calculate_funding_cost(100_000.0, 0.0001, 3, PositionSide.LONG)
        assert cost == pytest.approx(30.0)

    def test_short_receives_positive_rate(self):
        """正费率空头收：成本为负=净收入。"""
        cost = calculate_funding_cost(100_000.0, 0.0001, 3, PositionSide.SHORT)
        assert cost == pytest.approx(-30.0)

    def test_negative_rate_long_receives(self):
        cost = calculate_funding_cost(100_000.0, -0.0001, 3, PositionSide.LONG)
        assert cost == pytest.approx(-30.0)

    def test_zero_periods_no_cost(self):
        assert calculate_funding_cost(100_000.0, 0.0001, 0) == 0.0

    def test_zero_rate_no_cost(self):
        assert calculate_funding_cost(100_000.0, 0.0, 10) == 0.0

    def test_cost_scales_linearly(self):
        c1 = calculate_funding_cost(100_000.0, 0.0001, 1)
        c3 = calculate_funding_cost(100_000.0, 0.0001, 3)
        assert c3 == pytest.approx(3 * c1)

    def test_invalid_notional(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_funding_cost(0.0, 0.0001, 3)

    def test_invalid_periods(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_funding_cost(100_000.0, 0.0001, -1)


class TestMarginRatio:
    def test_normal(self):
        """margin_ratio = notional * mmr / balance。"""
        ratio = calculate_margin_ratio(1_000.0, 100_000.0, 0.004)
        assert ratio == pytest.approx(0.4)

    def test_liquidation_threshold(self):
        """ratio >= 1 → 爆仓线。"""
        ratio = calculate_margin_ratio(400.0, 100_000.0, 0.004)
        assert ratio == pytest.approx(1.0)

    def test_zero_balance_is_inf(self):
        """保证金余额 <=0 视为穿仓，返回 inf。"""
        assert calculate_margin_ratio(0.0, 100_000.0, 0.004) == math.inf
        assert calculate_margin_ratio(-10.0, 100_000.0, 0.004) == math.inf

    def test_invalid_notional(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_margin_ratio(1_000.0, 0.0, 0.004)

    def test_invalid_mmr(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_margin_ratio(1_000.0, 100_000.0, -0.01)


class TestDistanceToLiquidation:
    def test_long_safe(self):
        d = calculate_distance_to_liquidation(10_000.0, 9_040.0, PositionSide.LONG)
        assert d == pytest.approx(0.096)

    def test_short_safe(self):
        d = calculate_distance_to_liquidation(10_000.0, 10_960.0, PositionSide.SHORT)
        assert d == pytest.approx(0.096)

    def test_long_crossed_negative(self):
        """标记价跌破爆仓价 → 距离为负。"""
        d = calculate_distance_to_liquidation(9_000.0, 9_040.0, PositionSide.LONG)
        assert d < 0

    def test_short_crossed_negative(self):
        d = calculate_distance_to_liquidation(11_000.0, 10_960.0, PositionSide.SHORT)
        assert d < 0

    def test_invalid_mark_price(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_distance_to_liquidation(0.0, 9_040.0)

    def test_invalid_liq_price(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            calculate_distance_to_liquidation(10_000.0, -1.0)


class TestAssessLeveragePosition:
    def _assess(self, **overrides):
        kwargs = dict(
            side=PositionSide.LONG,
            entry_price=10_000.0,
            mark_price=10_000.0,
            leverage=10.0,
            position_notional=100_000.0,
            margin_balance=2_000.0,
            funding_rate=0.0001,
            holding_periods=3,
        )
        kwargs.update(overrides)
        return assess_leverage_position(**kwargs)

    def test_snapshot_aggregation(self):
        """聚合快照：mmr 落档 0.005（10 万档），爆仓价/成本/指标一致。"""
        s = self._assess()
        assert s.maintenance_margin_rate == pytest.approx(0.005)
        assert s.liquidation_price == pytest.approx(9_050.0)
        assert s.margin_ratio == pytest.approx(0.25)  # 500/2000
        assert s.distance_to_liquidation == pytest.approx(0.095)
        assert s.funding_cost == pytest.approx(30.0)
        assert s.risk_level == "SAFE"

    def test_risk_level_warning(self):
        s = self._assess(margin_balance=1_000.0)  # ratio=0.5
        assert s.risk_level == "WARNING"

    def test_risk_level_critical(self):
        s = self._assess(margin_balance=625.0)  # ratio=0.8
        assert s.risk_level == "CRITICAL"

    def test_risk_level_liquidated(self):
        s = self._assess(margin_balance=500.0)  # ratio=1.0
        assert s.risk_level == "LIQUIDATED"

    def test_risk_level_liquidated_zero_balance(self):
        s = self._assess(margin_balance=0.0)
        assert s.margin_ratio == math.inf
        assert s.risk_level == "LIQUIDATED"

    def test_short_position(self):
        s = self._assess(side=PositionSide.SHORT)
        assert s.liquidation_price == pytest.approx(10_950.0)
        assert s.funding_cost == pytest.approx(-30.0)
        assert s.distance_to_liquidation == pytest.approx(0.095)

    def test_large_notional_higher_tier(self):
        """大名义价值落高档 → 爆仓价更贴近开仓价。"""
        s = self._assess(position_notional=2_000_000.0)  # mmr=0.025
        assert s.maintenance_margin_rate == pytest.approx(0.025)
        assert s.liquidation_price == pytest.approx(9_250.0)

    def test_invalid_input_propagates(self):
        with pytest.raises(InvalidLeverageRiskInputError):
            self._assess(entry_price=-1.0)
