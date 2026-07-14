# [A_test] module_id: SRC-TST-1209 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md | §test
# [MODULE] zephyr.l07_post_trade_analytics
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l07_post_trade_analytics.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

l07 = pytest.importorskip("zephyr.l07_post_trade_analytics", reason="l07-post-trade-analytics not importable")

from zephyr.reporting.analytics_base import (
    AttributionEngineBase,
    TCAEngineBase,
)
from zephyr.shared.contracts.performance_attribution_report import (
    PerformanceAttributionReport,
)
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderType


def _make_fill(
    fill_id="f-001",
    symbol="AAPL",
    fill_price=Decimal("100.50"),
    filled_quantity=Decimal("100"),
    order_id="ord-001",
) -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=fill_price,
        fill_timestamp=datetime.now(UTC),
        filled_quantity=filled_quantity,
        idempotency_key="ik-fill",
        order_id=order_id,
        strategy_id="strat-1",
        symbol=symbol,
    )


def _make_order(
    order_id="ord-001",
    symbol="AAPL",
    side=OrderSide.BUY,
    quantity=Decimal("100"),
    limit_price=Decimal("100"),
) -> Order:
    return Order(
        order_id=order_id,
        symbol=symbol,
        strategy_id="strat-1",
        side=side,
        order_type=OrderType.MARKET,
        quantity=quantity,
        limit_price=limit_price,
        idempotency_key="ik-ord",
    )


class _ConcreteTCAEngine(TCAEngineBase):
    def analyze(self, fill, order, idempotency_key):
        slippage = 0.0
        if order.limit_price and order.limit_price > 0:
            slippage = float((fill.fill_price - order.limit_price) / order.limit_price * Decimal("10000"))
        return ExecutionReport(
            order_id=order.order_id,
            symbol=fill.symbol,
            direction="BUY",
            intended_quantity=int(order.quantity),
            actual_quantity=int(fill.filled_quantity),
            intended_price=order.limit_price or Decimal("0"),
            vwap_price=fill.fill_price,
            slippage_bps=slippage,
            commission=fill.commission,
            execution_start=fill.fill_timestamp.isoformat(),
            execution_end=fill.fill_timestamp.isoformat(),
            broker_id="simulation",
            idempotency_key=idempotency_key,
        )


class _ConcreteAttributionEngine(AttributionEngineBase):
    def attribute(self, portfolio_id, period_start, period_end, idempotency_key):
        return PerformanceAttributionReport(
            portfolio_id=portfolio_id,
            period_start=period_start,
            period_end=period_end,
            total_return=0.05,
            allocation_effect=0.02,
            selection_effect=0.025,
            interaction_effect=0.005,
            transaction_cost_drag=-0.001,
            idempotency_key=idempotency_key,
        )


class TestTCAEngineBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            TCAEngineBase()

    def test_analyze_returns_execution_report(self):
        engine = _ConcreteTCAEngine()
        fill = _make_fill()
        order = _make_order()
        report = engine.analyze(fill, order, "ik-test")
        assert isinstance(report, ExecutionReport)
        assert report.order_id == "ord-001"
        assert report.symbol == "AAPL"

    def test_analyze_slippage_positive(self):
        engine = _ConcreteTCAEngine()
        fill = _make_fill(fill_price=Decimal("101"))
        order = _make_order(limit_price=Decimal("100"))
        report = engine.analyze(fill, order, "ik-test")
        assert report.slippage_bps > 0

    def test_analyze_slippage_zero(self):
        engine = _ConcreteTCAEngine()
        fill = _make_fill(fill_price=Decimal("100"))
        order = _make_order(limit_price=Decimal("100"))
        report = engine.analyze(fill, order, "ik-test")
        assert report.slippage_bps == 0.0

    def test_analyze_batch_not_implemented(self):
        engine = _ConcreteTCAEngine()
        with pytest.raises(NotImplementedError):
            engine.analyze_batch([], {}, "ik-test")

    def test_analyze_with_no_limit_price(self):
        engine = _ConcreteTCAEngine()
        fill = _make_fill(fill_price=Decimal("100"))
        order = _make_order()
        order.limit_price = None
        report = engine.analyze(fill, order, "ik-test")
        assert report.slippage_bps == 0.0


class TestAttributionEngineBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            AttributionEngineBase()

    def test_attribute_returns_report(self):
        engine = _ConcreteAttributionEngine()
        report = engine.attribute("port-1", "2026-01-01", "2026-03-31", "ik-attr")
        assert isinstance(report, PerformanceAttributionReport)
        assert report.portfolio_id == "port-1"
        assert report.total_return == 0.05

    def test_attribute_effects_sum(self):
        engine = _ConcreteAttributionEngine()
        report = engine.attribute("port-1", "2026-01-01", "2026-03-31", "ik-attr")
        expected_total = report.allocation_effect + report.selection_effect + report.interaction_effect
        assert abs(report.total_return - expected_total) < 1e-9

    def test_attribute_idempotency_key(self):
        engine = _ConcreteAttributionEngine()
        report = engine.attribute("port-1", "2026-01-01", "2026-03-31", "ik-unique")
        assert report.idempotency_key == "ik-unique"

    def test_attribute_period(self):
        engine = _ConcreteAttributionEngine()
        report = engine.attribute("port-1", "2026-01-01", "2026-06-30", "ik-attr")
        assert report.period_start == "2026-01-01"
        assert report.period_end == "2026-06-30"


class TestExecutionReport:
    def test_creation(self):
        r = ExecutionReport(
            order_id="o1",
            symbol="AAPL",
            direction="BUY",
            intended_quantity=100,
            actual_quantity=100,
            intended_price=Decimal("100"),
            vwap_price=Decimal("100.5"),
            slippage_bps=5.0,
            commission=Decimal("3"),
            execution_start="2026-01-01T10:00:00",
            execution_end="2026-01-01T10:05:00",
            broker_id="sim",
            idempotency_key="ik",
        )
        assert r.order_id == "o1"

    def test_frozen(self):
        r = ExecutionReport(
            order_id="o1",
            symbol="AAPL",
            direction="BUY",
            intended_quantity=100,
            actual_quantity=100,
            intended_price=Decimal("100"),
            vwap_price=Decimal("100"),
            slippage_bps=0.0,
            commission=Decimal("0"),
            execution_start="",
            execution_end="",
            broker_id="sim",
            idempotency_key="ik",
        )
        with pytest.raises(AttributeError):
            r.order_id = "other"


class TestPerformanceAttributionReport:
    def test_creation(self):
        r = PerformanceAttributionReport(
            portfolio_id="p1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            total_return=0.05,
            allocation_effect=0.02,
            selection_effect=0.025,
            interaction_effect=0.005,
            transaction_cost_drag=-0.001,
            idempotency_key="ik",
        )
        assert r.portfolio_id == "p1"
        assert r.factor_contributions == {}

    def test_frozen(self):
        r = PerformanceAttributionReport(
            portfolio_id="p1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            total_return=0.05,
            allocation_effect=0.02,
            selection_effect=0.025,
            interaction_effect=0.005,
            transaction_cost_drag=-0.001,
            idempotency_key="ik",
        )
        with pytest.raises(AttributeError):
            r.portfolio_id = "other"

    def test_with_factor_contributions(self):
        r = PerformanceAttributionReport(
            portfolio_id="p1",
            period_start="2026-01-01",
            period_end="2026-03-31",
            total_return=0.05,
            allocation_effect=0.02,
            selection_effect=0.025,
            interaction_effect=0.005,
            transaction_cost_drag=-0.001,
            idempotency_key="ik",
            factor_contributions={"momentum": 0.03, "value": 0.02},
        )
        assert len(r.factor_contributions) == 2
