# [BLUEPRINT] MOD-PF-030 | docs/03_modules/_domain_portfolio_core/performance_attribution_engine/blueprint.md
# [MODULE] tests.pf_core.test_shadow_portfolio
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] pytest; zephyr.pf_core.core.shadow_portfolio
# [CONSUMERS] FAC-E9 影子组合引擎守卫（四分解守恒/方向语义/降级模式/双适配器）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 纯函数零副作用零网络零库；守恒恒等式在 BUY/SELL 两向都必须对平；
#   缺决策锚=降级出 unavailable 而非伪造；strict 模式锚缺必抛
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest 断言失败即红
# [TESTS] self
# [A_module] module_id=MOD-PF-030-T | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""shadow_portfolio 引擎测试——四分解守恒/不利为正/降级与 strict/供数适配。"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from zephyr.pf_core.core.shadow_portfolio import (
    ShadowDataIncompleteError,
    ShadowDecision,
    ShadowFill,
    ShadowPortfolioEngine,
    from_execution_reports,
    from_sim_trade_log,
)

_T0 = datetime(2026, 9, 26, 14, 55, tzinfo=UTC)
_T1 = datetime(2026, 9, 26, 14, 57, tzinfo=UTC)


class TestFourWayDecomposition:
    def test_buy_delay_and_execution_unfavorable(self):
        """BUY：决策 10 元，单笔 11 成交（首笔=均价：延迟 100 全额、执行 0），度量 12。"""
        engine = ShadowPortfolioEngine()
        c = engine.compare_symbol(
            ShadowDecision(symbol="600000.SH", side="BUY", quantity=100, decision_price=10.0, decision_ts=_T0),
            [ShadowFill(quantity=100, price=11.0, fee=5.0, ts=_T1)],
            measurement_price=12.0,
        )
        assert c.delay_cost == pytest.approx(100.0)
        assert c.execution_cost == pytest.approx(0.0)
        assert c.opportunity_cost == pytest.approx(0.0)
        assert c.fee_cost == pytest.approx(5.0)
        assert c.total_shortfall == pytest.approx(105.0)
        assert c.shadow_pnl - c.actual_pnl == pytest.approx(c.total_shortfall)  # 守恒

    def test_sell_direction_unfavorable_positive(self):
        """SELL：决策 10 元卖，单笔 9.5 成交（延迟 50 不利），度量 9。"""
        engine = ShadowPortfolioEngine()
        c = engine.compare_symbol(
            ShadowDecision(symbol="000001.SZ", side="SELL", quantity=100, decision_price=10.0, decision_ts=_T0),
            [ShadowFill(quantity=100, price=9.5, fee=5.0, ts=_T1)],
            measurement_price=9.0,
        )
        assert c.delay_cost == pytest.approx(50.0)
        assert c.execution_cost == pytest.approx(0.0)
        assert c.total_shortfall == pytest.approx(55.0)
        assert c.shadow_pnl - c.actual_pnl == pytest.approx(c.total_shortfall)

    def test_opportunity_cost_on_partial_fill(self):
        """BUY：计划 100 只成交 60，度量 12>决策 10 → 机会成本=2×40=80 不利。"""
        engine = ShadowPortfolioEngine()
        c = engine.compare_symbol(
            ShadowDecision(symbol="600000.SH", side="BUY", quantity=100, decision_price=10.0, decision_ts=_T0),
            [ShadowFill(quantity=60, price=10.0, fee=3.0, ts=_T1)],
            measurement_price=12.0,
        )
        assert c.filled_quantity == 60
        assert c.opportunity_cost == pytest.approx(80.0)
        assert c.shadow_pnl - c.actual_pnl == pytest.approx(c.total_shortfall)

    def test_multi_fill_first_price_is_delay_anchor(self):
        engine = ShadowPortfolioEngine()
        c = engine.compare_symbol(
            ShadowDecision(symbol="600000.SH", side="BUY", quantity=100, decision_price=10.0, decision_ts=_T0),
            [
                ShadowFill(quantity=50, price=10.5, fee=2.5, ts=_T1),
                ShadowFill(quantity=50, price=11.5, fee=2.5),
            ],
            measurement_price=12.0,
        )
        assert c.delay_cost == pytest.approx(50.0)  # (10.5-10)×100
        assert c.execution_cost == pytest.approx(50.0)  # (11-10.5)×100


class TestDegradedAndStrict:
    def test_missing_decision_anchor_degrades_not_fabricates(self):
        engine = ShadowPortfolioEngine()
        c = engine.compare_symbol(
            ShadowDecision(symbol="600000.SH", side="BUY", quantity=100, decision_price=None),
            [ShadowFill(quantity=100, price=11.0, fee=5.0, ts=_T1)],
            measurement_price=12.0,
        )
        assert c.decision_available is False
        assert c.delay_cost is None and c.execution_cost is None and c.opportunity_cost is None
        assert c.total_shortfall is None
        assert c.fee_cost == pytest.approx(5.0)  # 费用面真值仍出
        assert any("decision_anchor_missing" in n for n in c.notes)

    def test_strict_mode_raises_on_missing_anchor(self):
        engine = ShadowPortfolioEngine()
        with pytest.raises(ShadowDataIncompleteError):
            engine.compare_symbol(
                ShadowDecision(symbol="600000.SH", side="BUY", quantity=100, decision_price=None),
                [ShadowFill(quantity=100, price=11.0)],
                measurement_price=12.0,
                strict=True,
            )

    def test_empty_actual_leg_rejected(self):
        engine = ShadowPortfolioEngine()
        with pytest.raises(ShadowDataIncompleteError):
            engine.compare_symbol(
                ShadowDecision(symbol="600000.SH", side="BUY", quantity=100, decision_price=10.0),
                [],
                measurement_price=12.0,
            )

    def test_side_enum_guard(self):
        engine = ShadowPortfolioEngine()
        with pytest.raises(ShadowDataIncompleteError):
            engine.compare_symbol(
                ShadowDecision(symbol="600000.SH", side="HOLD", quantity=100, decision_price=10.0),
                [ShadowFill(quantity=100, price=10.0)],
                measurement_price=12.0,
            )


class TestAdapters:
    def test_from_execution_reports_full_decomposition(self):
        class _Rep:
            order_id = "o1"
            symbol = "600000.SH"
            direction = "BUY"
            intended_quantity = 100
            actual_quantity = 100
            intended_price = 10.0
            vwap_price = 10.6
            commission = 5.0
            decision_timestamp = "2026-09-26T14:55:00+00:00"

        out = from_execution_reports([_Rep()], {"600000.SH": 12.0})
        assert len(out) == 1
        c = out[0]
        assert c.decision_available is True
        # 单聚合 fill：首笔=均价 → 延迟=60，执行=0
        assert c.delay_cost == pytest.approx(60.0)
        assert c.execution_cost == pytest.approx(0.0)
        assert c.fee_cost == pytest.approx(5.0)

    def test_from_sim_trade_log_degraded_honest(self):
        rows = [
            {
                "strategy_id": "STR-A",
                "symbol": "600000",
                "action": "entry",
                "shares": 100.0,
                "price": 10.0,
                "cost_paid": 7.5,
            },
            {
                "strategy_id": "STR-A",
                "symbol": "600000",
                "action": "exit",
                "shares": 100.0,
                "price": 11.0,
                "cost_paid": 8.75,
            },
        ]
        out = from_sim_trade_log(rows, {"600000": 11.0})
        assert len(out) == 1
        c = out[0]
        assert c.decision_available is False  # 账本无决策锚——禁伪造零延迟
        assert c.fee_cost == pytest.approx(16.25)  # cost_paid 真值（禁复算成本常量）
        assert "STR-A" in c.symbol

    def test_portfolio_aggregate_sums_known_skips_missing(self):
        engine = ShadowPortfolioEngine()
        c1 = engine.compare_symbol(
            ShadowDecision(symbol="A", side="BUY", quantity=100, decision_price=10.0),
            [ShadowFill(quantity=100, price=11.0, fee=1.0)],
            measurement_price=12.0,
        )
        c2 = engine.compare_symbol(
            ShadowDecision(symbol="B", side="BUY", quantity=100, decision_price=None),
            [ShadowFill(quantity=100, price=11.0, fee=2.0)],
            measurement_price=12.0,
        )
        agg = engine.compare_portfolio([c1, c2])
        assert agg["total_shortfall"] == pytest.approx(c1.total_shortfall or 0.0)  # 降级件无 total，不并入
        assert agg["fee_cost"] == pytest.approx(3.0)  # 费用面真值逐件可加（1+2）
        assert agg["degraded_symbols"] == 1
