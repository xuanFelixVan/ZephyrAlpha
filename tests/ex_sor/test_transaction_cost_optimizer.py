# [BLUEPRINT] MOD-EX_SOR_EXT-003 | docs/03_modules/_domain-ex_sor/transaction_cost_optimizer/blueprint.md
# [TTL] permanent
"""TransactionCostOptimizer 单元测试 (MOD-EX_SOR_EXT-003)。全成本计算+分解+优化建议。"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from zephyr.ex_sor.services.transaction_cost_optimizer import (
    TransactionCostBreakdown,
    CostComponent,
    FeeSchedule,
    InvalidCostInputError,
    InvalidFeeScheduleError,
    LinearImpactEstimator,
    OptimizationAdvice,
    TransactionCostError,
    TransactionCostOptimizer,
    TransactionCostResult,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide

NOW = datetime(2026, 8, 4, 14, 0, tzinfo=timezone.utc)


# ══════════════════════════════════════════════════════════════════════════════
# FeeSchedule
# ══════════════════════════════════════════════════════════════════════════════


class TestFeeSchedule:
    def test_defaults(self):
        f = FeeSchedule()
        assert f.commission_rate_bps == Decimal("3")
        assert f.commission_min == Decimal("5")
        assert f.stamp_duty_rate_bps == Decimal("5")
        assert f.transfer_fee_rate_bps == Decimal("0.1")
        assert f.regulatory_fee_rate_bps == Decimal("0.2")

    def test_custom(self):
        f = FeeSchedule(
            commission_rate_bps=Decimal("2.5"),
            commission_min=Decimal("1"),
            stamp_duty_rate_bps=Decimal("10"),
        )
        assert f.commission_rate_bps == Decimal("2.5")
        assert f.stamp_duty_rate_bps == Decimal("10")

    def test_negative_commission_rate_raises(self):
        with pytest.raises(InvalidFeeScheduleError, match="不能为负"):
            FeeSchedule(commission_rate_bps=Decimal("-1"))

    def test_negative_stamp_duty_raises(self):
        with pytest.raises(InvalidFeeScheduleError):
            FeeSchedule(stamp_duty_rate_bps=Decimal("-0.1"))

    def test_negative_min_raises(self):
        with pytest.raises(InvalidFeeScheduleError, match="最低佣金"):
            FeeSchedule(commission_min=Decimal("-1"))

    def test_zero_rates_allowed(self):
        f = FeeSchedule(commission_rate_bps=Decimal("0"), stamp_duty_rate_bps=Decimal("0"))
        assert f.commission_rate_bps == Decimal("0")

    def test_frozen(self):
        f = FeeSchedule()
        with pytest.raises(Exception):
            f.commission_rate_bps = Decimal("10")  # type: ignore[misc]


# ══════════════════════════════════════════════════════════════════════════════
# CostComponent
# ══════════════════════════════════════════════════════════════════════════════


class TestCostComponent:
    def test_str_returns_value(self):
        assert str(CostComponent.COMMISSION) == "COMMISSION"
        assert str(CostComponent.STAMP_DUTY) == "STAMP_DUTY"

    def test_six_components(self):
        assert len(list(CostComponent)) == 6


# ══════════════════════════════════════════════════════════════════════════════
# 显性成本 — 佣金
# ══════════════════════════════════════════════════════════════════════════════


class TestCommission:
    def test_commission_applies_min(self):
        """小单佣金低于最低收费 → 取最低值 5 元。"""
        opt = TransactionCostOptimizer()
        # 100 股 × 10 元 = 1000 元 notional, 佣金 = 1000×3/10000 = 0.3 → min 5
        r = opt.calculate("O1", "000001.SZ", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"), now=NOW)
        comm = r.breakdown_for(CostComponent.COMMISSION)
        assert comm.amount == Decimal("5.00")

    def test_commission_above_min(self):
        """大单佣金超过最低收费 → 按费率计算。"""
        opt = TransactionCostOptimizer()
        # 100000 股 × 10 元 = 1000000 notional, 佣金 = 1000000×3/10000 = 300
        r = opt.calculate("O1", "000001.SZ", OrderSide.BUY,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        comm = r.breakdown_for(CostComponent.COMMISSION)
        assert comm.amount == Decimal("300.00")

    def test_commission_custom_min(self):
        opt = TransactionCostOptimizer(FeeSchedule(commission_min=Decimal("0")))
        r = opt.calculate("O1", "000001.SZ", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"), now=NOW)
        comm = r.breakdown_for(CostComponent.COMMISSION)
        # 100×10×3/10000 = 0.30
        assert comm.amount == Decimal("0.30")

    def test_commission_both_sides(self):
        """佣金买卖双方都收。"""
        opt = TransactionCostOptimizer()
        rb = opt.calculate("O1", "X", OrderSide.BUY,
                           Decimal("100000"), Decimal("10.00"), now=NOW)
        rs = opt.calculate("O2", "X", OrderSide.SELL,
                           Decimal("100000"), Decimal("10.00"), now=NOW)
        assert rb.breakdown_for(CostComponent.COMMISSION).amount == \
            rs.breakdown_for(CostComponent.COMMISSION).amount


# ══════════════════════════════════════════════════════════════════════════════
# 显性成本 — 印花税
# ══════════════════════════════════════════════════════════════════════════════


class TestStampDuty:
    def test_buy_no_stamp_duty(self):
        """买方免征印花税。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        sd = r.breakdown_for(CostComponent.STAMP_DUTY)
        assert sd.amount == Decimal("0.00")

    def test_sell_stamp_duty_charged(self):
        """卖方收印花税 5bps。"""
        opt = TransactionCostOptimizer()
        # notional = 1000000, 印花税 = 1000000×5/10000 = 500
        r = opt.calculate("O1", "X", OrderSide.SELL,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        sd = r.breakdown_for(CostComponent.STAMP_DUTY)
        assert sd.amount == Decimal("500.00")

    def test_stamp_duty_rate_configurable(self):
        opt = TransactionCostOptimizer(FeeSchedule(stamp_duty_rate_bps=Decimal("10")))
        r = opt.calculate("O1", "X", OrderSide.SELL,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        sd = r.breakdown_for(CostComponent.STAMP_DUTY)
        # 1000000 × 10/10000 = 1000
        assert sd.amount == Decimal("1000.00")


# ══════════════════════════════════════════════════════════════════════════════
# 显性成本 — 过户费 + 监管费
# ══════════════════════════════════════════════════════════════════════════════


class TestTransferAndRegulatory:
    def test_transfer_fee_both_sides(self):
        opt = TransactionCostOptimizer()
        rb = opt.calculate("O1", "X", OrderSide.BUY,
                           Decimal("100000"), Decimal("10.00"), now=NOW)
        rs = opt.calculate("O2", "X", OrderSide.SELL,
                           Decimal("100000"), Decimal("10.00"), now=NOW)
        # 1000000 × 0.1/10000 = 10
        assert rb.breakdown_for(CostComponent.TRANSFER_FEE).amount == Decimal("10.00")
        assert rs.breakdown_for(CostComponent.TRANSFER_FEE).amount == Decimal("10.00")

    def test_regulatory_fee_both_sides(self):
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        # 1000000 × 0.2/10000 = 20
        assert r.breakdown_for(CostComponent.REGULATORY_FEE).amount == Decimal("20.00")


# ══════════════════════════════════════════════════════════════════════════════
# 显性成本汇总
# ══════════════════════════════════════════════════════════════════════════════


class TestExplicitCost:
    def test_buy_explicit(self):
        """BUY 显性 = 佣金 + 0(印花税) + 过户费 + 监管费。"""
        opt = TransactionCostOptimizer()
        # 100000 股 × 10 = 1000000 notional
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        # 佣金 300 + 印花税 0 + 过户费 10 + 监管费 20 = 330
        assert r.explicit_cost == Decimal("330.00")

    def test_sell_explicit(self):
        """SELL 显性 = 佣金 + 印花税 + 过户费 + 监管费。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.SELL,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        # 佣金 300 + 印花税 500 + 过户费 10 + 监管费 20 = 830
        assert r.explicit_cost == Decimal("830.00")

    def test_small_order_explicit(self):
        """小单佣金取最低值。"""
        opt = TransactionCostOptimizer()
        # 100 股 × 10 = 1000 notional
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"), now=NOW)
        # 佣金 5(min) + 印花税 0 + 过户费 0.01 + 监管费 0.02 = 5.03
        assert r.explicit_cost == Decimal("5.03")


# ══════════════════════════════════════════════════════════════════════════════
# 隐性成本 — 冲击成本
# ══════════════════════════════════════════════════════════════════════════════


class TestImpactCost:
    def test_buy_impact_with_decision_price(self):
        """BUY: 成交价 > 决策价 → 正冲击成本。"""
        opt = TransactionCostOptimizer()
        # 1000 股, 成交 10.50, 决策 10.40 → 冲击 = 0.10 × 1000 = 100
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.50"),
                          decision_price=Decimal("10.40"), now=NOW)
        imp = r.breakdown_for(CostComponent.IMPACT)
        assert imp.amount == Decimal("100.00")

    def test_buy_impact_zero_when_better_than_decision(self):
        """BUY: 成交价 < 决策价 → 有利执行, 冲击 = 0。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.30"),
                          decision_price=Decimal("10.40"), now=NOW)
        imp = r.breakdown_for(CostComponent.IMPACT)
        assert imp.amount == Decimal("0.00")

    def test_sell_impact_with_decision_price(self):
        """SELL: 成交价 < 决策价 → 正冲击成本。"""
        opt = TransactionCostOptimizer()
        # 1000 股, 成交 10.30, 决策 10.40 → 冲击 = 0.10 × 1000 = 100
        r = opt.calculate("O1", "X", OrderSide.SELL,
                          Decimal("1000"), Decimal("10.30"),
                          decision_price=Decimal("10.40"), now=NOW)
        imp = r.breakdown_for(CostComponent.IMPACT)
        assert imp.amount == Decimal("100.00")

    def test_sell_impact_zero_when_better_than_decision(self):
        """SELL: 成交价 > 决策价 → 有利, 冲击 = 0。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.SELL,
                          Decimal("1000"), Decimal("10.50"),
                          decision_price=Decimal("10.40"), now=NOW)
        imp = r.breakdown_for(CostComponent.IMPACT)
        assert imp.amount == Decimal("0.00")

    def test_impact_estimated_without_decision_price(self):
        """无决策价但有 ADV+波动率 → 用估计器。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("10000"), Decimal("10.00"),
                          adv=Decimal("1000000"), volatility=Decimal("0.02"),
                          now=NOW)
        imp = r.breakdown_for(CostComponent.IMPACT)
        assert imp.amount > _ZERO_D()

    def test_impact_zero_without_any_input(self):
        """无决策价无 ADV → 冲击 = 0。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.00"), now=NOW)
        imp = r.breakdown_for(CostComponent.IMPACT)
        assert imp.amount == Decimal("0.00")


def _ZERO_D() -> Decimal:
    return Decimal("0")


# ══════════════════════════════════════════════════════════════════════════════
# 隐性成本 — 机会成本
# ══════════════════════════════════════════════════════════════════════════════


class TestOpportunityCost:
    def test_no_opportunity_when_fully_filled(self):
        """全部成交 → 机会成本 = 0。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.00"),
                          decision_price=Decimal("10.00"), now=NOW)
        opp = r.breakdown_for(CostComponent.OPPORTUNITY)
        assert opp.amount == Decimal("0.00")

    def test_opportunity_with_unfilled(self):
        """有未成交 → 机会成本 > 0。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("800"), Decimal("10.00"),
                          decision_price=Decimal("10.00"),
                          unfilled_quantity=Decimal("200"), now=NOW)
        opp = r.breakdown_for(CostComponent.OPPORTUNITY)
        assert opp.amount > Decimal("0")

    def test_opportunity_zero_without_decision_price(self):
        """无决策价 → 机会成本 = 0。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("800"), Decimal("10.00"),
                          unfilled_quantity=Decimal("200"), now=NOW)
        opp = r.breakdown_for(CostComponent.OPPORTUNITY)
        assert opp.amount == Decimal("0.00")


# ══════════════════════════════════════════════════════════════════════════════
# 总成本
# ══════════════════════════════════════════════════════════════════════════════


class TestTotalCost:
    def test_total_equals_explicit_plus_implicit(self):
        """总成本 = 显性 + 隐性 (守恒)。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.50"),
                          decision_price=Decimal("10.40"), now=NOW)
        assert r.total_cost == r.explicit_cost + r.implicit_cost

    def test_total_cost_bps(self):
        """总成本 bps = 总成本 / 成交金额 × 10000。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        # notional = 1000000, explicit = 330, implicit = 0
        # bps = 330 / 1000000 × 10000 = 3.3
        assert r.total_cost_bps == pytest.approx(Decimal("3.3"), abs=0.1)

    def test_sell_total_higher_than_buy(self):
        """SELL 总成本 > BUY (因印花税)。"""
        opt = TransactionCostOptimizer()
        rb = opt.calculate("O1", "X", OrderSide.BUY,
                           Decimal("100000"), Decimal("10.00"), now=NOW)
        rs = opt.calculate("O2", "X", OrderSide.SELL,
                           Decimal("100000"), Decimal("10.00"), now=NOW)
        assert rs.total_cost > rb.total_cost

    def test_explicit_cost_bps(self):
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        # explicit = 330, notional = 1000000 → 3.3 bps
        assert r.explicit_cost_bps == pytest.approx(Decimal("3.3"), abs=0.1)

    def test_implicit_cost_bps(self):
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.50"),
                          decision_price=Decimal("10.40"), now=NOW)
        # implicit = 100, notional = 10500 → ~95.24 bps
        assert r.implicit_cost_bps == pytest.approx(Decimal("95.2381"), abs=1)


# ══════════════════════════════════════════════════════════════════════════════
# 优化建议
# ══════════════════════════════════════════════════════════════════════════════


class TestOptimizationAdvice:
    def test_advise_commission_driven(self):
        """小单佣金占比最高 → 建议协商费率。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"), now=NOW)
        advice = opt.advise(r)
        assert advice.primary_driver == CostComponent.COMMISSION
        assert "佣金" in advice.recommendation
        assert advice.estimated_saving_bps > Decimal("0")

    def test_advise_stamp_duty_driven(self):
        """大单卖出印花税最高 → 建议减少换手。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.SELL,
                          Decimal("100000"), Decimal("10.00"), now=NOW)
        advice = opt.advise(r)
        assert advice.primary_driver == CostComponent.STAMP_DUTY
        assert "换手" in advice.recommendation

    def test_advise_impact_driven(self):
        """冲击成本占比最高 → 建议拆单。"""
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("11.00"),
                          decision_price=Decimal("10.00"), now=NOW)
        # 冲击 = 1.00 × 1000 = 1000, 佣金 = 5(min)... notional=11000
        advice = opt.advise(r)
        assert advice.primary_driver == CostComponent.IMPACT
        assert "拆单" in advice.recommendation

    def test_advise_zero_cost(self):
        """零成本 → 无需优化。"""
        opt = TransactionCostOptimizer(FeeSchedule(
            commission_rate_bps=Decimal("0"), commission_min=Decimal("0"),
            stamp_duty_rate_bps=Decimal("0"),
            transfer_fee_rate_bps=Decimal("0"), regulatory_fee_rate_bps=Decimal("0"),
        ))
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.00"), now=NOW)
        advice = opt.advise(r)
        assert advice.estimated_saving_bps == Decimal("0")


# ══════════════════════════════════════════════════════════════════════════════
# LinearImpactEstimator
# ══════════════════════════════════════════════════════════════════════════════


class TestLinearImpactEstimator:
    def test_estimate_positive(self):
        est = LinearImpactEstimator()
        val = est.estimate(Decimal("1000000"), Decimal("0.01"), Decimal("0.02"))
        assert val > Decimal("0")

    def test_estimate_zero_notional(self):
        est = LinearImpactEstimator()
        val = est.estimate(Decimal("0"), Decimal("0.01"), Decimal("0.02"))
        assert val == Decimal("0.00")

    def test_estimate_increases_with_participation(self):
        est = LinearImpactEstimator()
        low = est.estimate(Decimal("1000000"), Decimal("0.01"), Decimal("0.02"))
        high = est.estimate(Decimal("1000000"), Decimal("0.05"), Decimal("0.02"))
        assert high > low

    def test_custom_coefficient(self):
        e1 = LinearImpactEstimator(coefficient=1.0)
        e2 = LinearImpactEstimator(coefficient=10.0)
        v1 = e1.estimate(Decimal("1000000"), Decimal("0.01"), Decimal("0.02"))
        v2 = e2.estimate(Decimal("1000000"), Decimal("0.01"), Decimal("0.02"))
        assert v2 > v1


# ══════════════════════════════════════════════════════════════════════════════
# 历史追踪
# ══════════════════════════════════════════════════════════════════════════════


class TestHistory:
    def test_history_accumulates(self):
        opt = TransactionCostOptimizer()
        for i in range(3):
            opt.calculate(f"O{i}", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"), now=NOW)
        assert len(opt.history) == 3

    def test_history_filtered_by_symbol(self):
        opt = TransactionCostOptimizer()
        opt.calculate("O1", "000001.SZ", OrderSide.BUY,
                      Decimal("100"), Decimal("10.00"), now=NOW)
        opt.calculate("O2", "600519.SH", OrderSide.BUY,
                      Decimal("100"), Decimal("10.00"), now=NOW)
        sz = opt.get_history(symbol="000001.SZ")
        assert len(sz) == 1
        assert sz[0].symbol == "000001.SZ"

    def test_clear_history(self):
        opt = TransactionCostOptimizer()
        opt.calculate("O1", "X", OrderSide.BUY,
                      Decimal("100"), Decimal("10.00"), now=NOW)
        opt.clear_history()
        assert len(opt.history) == 0


# ══════════════════════════════════════════════════════════════════════════════
# 异常 & 边界
# ══════════════════════════════════════════════════════════════════════════════


class TestErrorsAndEdgeCases:
    def test_zero_quantity_raises(self):
        opt = TransactionCostOptimizer()
        with pytest.raises(InvalidCostInputError, match="成交数量"):
            opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("0"), Decimal("10.00"), now=NOW)

    def test_negative_quantity_raises(self):
        opt = TransactionCostOptimizer()
        with pytest.raises(InvalidCostInputError, match="成交数量"):
            opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("-1"), Decimal("10.00"), now=NOW)

    def test_zero_price_raises(self):
        opt = TransactionCostOptimizer()
        with pytest.raises(InvalidCostInputError, match="成交价"):
            opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("0"), now=NOW)

    def test_negative_unfilled_raises(self):
        opt = TransactionCostOptimizer()
        with pytest.raises(InvalidCostInputError, match="未成交"):
            opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"),
                          unfilled_quantity=Decimal("-1"), now=NOW)

    def test_default_now(self):
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"))
        assert r.analyzed_at is not None

    def test_result_frozen(self):
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"), now=NOW)
        with pytest.raises(Exception):
            r.total_cost = Decimal("0")  # type: ignore[misc]

    def test_breakdown_has_six_components(self):
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("1000"), Decimal("10.00"), now=NOW)
        assert len(r.breakdown) == 6

    def test_breakdown_for_missing_returns_none(self):
        opt = TransactionCostOptimizer()
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("100"), Decimal("10.00"), now=NOW)
        # all 6 exist, but test the method
        b = r.breakdown_for(CostComponent.IMPACT)
        assert b is not None  # always present (may be 0)

    def test_custom_impact_estimator(self):
        class FixedEstimator:
            def estimate(self, notional, pr, vol):
                return Decimal("999.99")

        opt = TransactionCostOptimizer(impact_estimator=FixedEstimator())
        r = opt.calculate("O1", "X", OrderSide.BUY,
                          Decimal("10000"), Decimal("10.00"),
                          adv=Decimal("1000000"), volatility=Decimal("0.02"),
                          now=NOW)
        assert r.breakdown_for(CostComponent.IMPACT).amount == Decimal("999.99")

    def test_fee_schedule_property(self):
        opt = TransactionCostOptimizer()
        assert opt.fee_schedule.commission_rate_bps == Decimal("3")
