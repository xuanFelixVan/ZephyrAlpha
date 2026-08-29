# [BLUEPRINT] MOD-L06-003 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_eod_reconciliation
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.eod_reconciliation; zephyr.ex_core.position_reconciler; zephyr.ex_core.position_tracker.tracker; zephyr.ex_core.order_manager
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""EodReconciler 单元测试 — 40 号 §6.1 gap 10 盘后全量对账 Phase 2。

覆盖：持仓全量对账委托 / 资金核对（容差/跳过/差异告警）/ 未成交订单日终
转 EXPIRED（幂等）/ T+1 以券商为准对齐（显式开启 + Fail-Closed）/
输入校验 / 结果不可变 / 告警吞没。
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.eod_reconciliation import (
    EodReconciliationError,
    EodReconcileResult,
    EodReconciler,
)
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_reconciler import PositionReconciler
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.position import PositionSnapshot

# ── helpers ──


def make_snapshot(holdings: dict[str, Decimal], cash: Decimal = Decimal("1000000")) -> PositionSnapshot:
    return PositionSnapshot(
        as_of_timestamp=datetime.now(UTC),
        idempotency_key="test-key",
        portfolio_id="test-portfolio",
        cash=cash,
        holdings=dict(holdings),
        market_values={},
        total_market_value=Decimal("0"),
    )


class FakeSource:
    """可编程 PositionSource。"""

    def __init__(self, holdings: dict[str, Decimal] | None = None) -> None:
        self._holdings = dict(holdings) if holdings else {}

    def get_positions(self) -> PositionSnapshot:
        return make_snapshot(self._holdings)


def make_reconciler(
    system_holdings: dict[str, Decimal] | None = None,
    broker_holdings: dict[str, Decimal] | None = None,
    **kwargs,
) -> EodReconciler:
    rec = PositionReconciler(FakeSource(system_holdings), FakeSource(broker_holdings))
    return EodReconciler(position_reconciler=rec, **kwargs)


def make_order(om: OrderManager, status: OrderStatus = OrderStatus.PENDING) -> str:
    order = om.create_order(
        symbol="600000.SH",
        strategy_id="test",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("100"),
        limit_price=Decimal("10.00"),
    )
    order.status = status
    return order.order_id


# ── 输入校验（Fail-Closed）──


class TestInputValidation:
    def test_empty_trade_date_rejected(self):
        eod = make_reconciler()
        with pytest.raises(EodReconciliationError):
            eod.run_eod(trade_date="")

    def test_negative_cash_tolerance_rejected(self):
        rec = PositionReconciler(FakeSource(), FakeSource())
        with pytest.raises(EodReconciliationError):
            EodReconciler(position_reconciler=rec, cash_tolerance=Decimal("-0.01"))

    def test_missing_position_reconciler_rejected(self):
        with pytest.raises(EodReconciliationError):
            EodReconciler(position_reconciler=None)  # type: ignore[arg-type]

    def test_broker_cash_without_tracker_rejected(self):
        eod = make_reconciler()
        with pytest.raises(EodReconciliationError, match="position_tracker"):
            eod.run_eod(trade_date="2026-08-28", broker_cash=Decimal("100"))

    def test_align_without_settled_holdings_rejected(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        eod = make_reconciler(position_tracker=tracker)
        with pytest.raises(EodReconciliationError, match="align_to_broker"):
            eod.run_eod(trade_date="2026-08-28", align_to_broker=True)

    def test_align_without_tracker_rejected(self):
        eod = make_reconciler()
        with pytest.raises(EodReconciliationError, match="align_to_broker"):
            eod.run_eod(
                trade_date="2026-08-28",
                broker_settled_holdings={"600000.SH": {"qty": 100, "avg_cost": "10"}},
                align_to_broker=True,
            )


# ── 持仓 + 资金对账 ──


class TestPositionAndCashReconcile:
    def test_full_match(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        eod = make_reconciler(
            {"600000.SH": Decimal("100")},
            {"600000.SH": Decimal("100")},
            position_tracker=tracker,
        )

        result = eod.run_eod(trade_date="2026-08-28", broker_cash=Decimal("1000000"))

        assert result.matched is True
        assert result.positions_matched is True
        assert result.position_drifts == ()
        assert result.cash_checked is True
        assert result.cash_matched is True
        assert result.cash_diff == Decimal("0")
        assert result.t1_aligned is False
        assert result.expired_order_ids == ()

    def test_position_drift_unmatched_and_alerted(self):
        alerts: list[EodReconcileResult] = []
        eod = make_reconciler(
            {"600000.SH": Decimal("100")},
            {"600000.SH": Decimal("200")},
            alert_sink=alerts.append,
        )

        result = eod.run_eod(trade_date="2026-08-28")

        assert result.matched is False
        assert result.positions_matched is False
        assert len(result.position_drifts) == 1
        assert result.position_drifts[0].diff == Decimal("-100")
        assert result.frozen_symbols == frozenset({"600000.SH"})
        assert len(alerts) == 1

    def test_cash_drift_within_tolerance_matched(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        eod = make_reconciler(position_tracker=tracker, cash_tolerance=Decimal("0.01"))

        result = eod.run_eod(trade_date="2026-08-28", broker_cash=Decimal("999999.995"))

        assert result.cash_matched is True
        assert result.matched is True

    def test_cash_drift_beyond_tolerance_unmatched(self):
        alerts: list[EodReconcileResult] = []
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        eod = make_reconciler(position_tracker=tracker, alert_sink=alerts.append)

        result = eod.run_eod(trade_date="2026-08-28", broker_cash=Decimal("999999"))

        assert result.cash_matched is False
        assert result.cash_diff == Decimal("1")
        assert result.matched is False
        assert len(alerts) == 1

    def test_cash_check_skipped_when_broker_cash_absent(self):
        eod = make_reconciler(position_tracker=PositionTracker())

        result = eod.run_eod(trade_date="2026-08-28")

        assert result.cash_checked is False
        assert result.cash_matched is None
        assert result.cash_diff is None
        assert result.matched is True

    def test_alert_sink_exception_swallowed(self):
        def _boom(result: EodReconcileResult) -> None:
            raise RuntimeError("alert exploded")

        eod = make_reconciler({"A": Decimal("1")}, {"A": Decimal("2")}, alert_sink=_boom)

        result = eod.run_eod(trade_date="2026-08-28")  # 不抛

        assert result.matched is False


# ── 未成交订单日终转 EXPIRED ──


class TestExpireOpenOrders:
    def test_non_terminal_orders_expired(self):
        om = OrderManager()
        id_pending = make_order(om, OrderStatus.PENDING)
        id_submitted = make_order(om, OrderStatus.SUBMITTED)
        id_partial = make_order(om, OrderStatus.PARTIAL)
        id_filled = make_order(om, OrderStatus.FILLED)
        id_cancelled = make_order(om, OrderStatus.CANCELLED)
        eod = make_reconciler(order_manager=om)

        result = eod.run_eod(trade_date="2026-08-28")

        assert set(result.expired_order_ids) == {id_pending, id_submitted, id_partial}
        assert om.get_order(id_filled).status is OrderStatus.FILLED  # type: ignore[union-attr]
        assert om.get_order(id_cancelled).status is OrderStatus.CANCELLED  # type: ignore[union-attr]
        assert om.get_order(id_pending).status is OrderStatus.EXPIRED  # type: ignore[union-attr]

    def test_expire_idempotent(self):
        om = OrderManager()
        make_order(om, OrderStatus.SUBMITTED)
        eod = make_reconciler(order_manager=om)

        first = eod.run_eod(trade_date="2026-08-28")
        second = eod.run_eod(trade_date="2026-08-28")

        assert len(first.expired_order_ids) == 1
        assert second.expired_order_ids == ()

    def test_no_order_manager_skips_expire(self):
        eod = make_reconciler()

        result = eod.run_eod(trade_date="2026-08-28")

        assert result.expired_order_ids == ()

    def test_order_manager_expire_open_orders_direct(self):
        """OrderManager.expire_open_orders 直接调用语义。"""
        om = OrderManager()
        make_order(om, OrderStatus.PENDING)
        make_order(om, OrderStatus.FILLED)

        expired = om.expire_open_orders()

        assert len(expired) == 1
        assert expired[0].status is OrderStatus.EXPIRED
        assert om.expire_open_orders() == []  # 幂等


# ── T+1 可用更新（以券商为准对齐）──


class TestT1AlignToBroker:
    def test_align_rebuilds_tracker_from_broker(self):
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        eod = make_reconciler(position_tracker=tracker)

        result = eod.run_eod(
            trade_date="2026-08-28",
            broker_cash=Decimal("500000"),
            broker_settled_holdings={"600000.SH": {"qty": 300, "avg_cost": "9.50"}},
            align_to_broker=True,
        )

        assert result.t1_aligned is True
        assert tracker.holdings == {"600000.SH": Decimal("300")}
        assert tracker.avg_costs == {"600000.SH": Decimal("9.50")}
        assert tracker.cash == Decimal("500000")

    def test_default_report_only_no_mutation(self):
        """默认 align_to_broker=False：仅报告，不动系统账（dry-run 语义）。"""
        tracker = PositionTracker(initial_cash=Decimal("1000000"))
        eod = make_reconciler(position_tracker=tracker)

        result = eod.run_eod(
            trade_date="2026-08-28",
            broker_cash=Decimal("1"),
            broker_settled_holdings={"600000.SH": {"qty": 300, "avg_cost": "9.50"}},
        )

        assert result.t1_aligned is False
        assert tracker.holdings == {}
        assert tracker.cash == Decimal("1000000")
        assert result.cash_matched is False  # 差异如实披露


# ── 结果不可变 ──


class TestResultFrozen:
    def test_result_is_frozen(self):
        eod = make_reconciler()
        result = eod.run_eod(trade_date="2026-08-28")

        with pytest.raises(AttributeError):
            result.matched = False  # type: ignore[misc]

    def test_clock_injected(self):
        fixed = datetime(2026, 8, 28, 16, 0, tzinfo=UTC)
        eod = make_reconciler(clock=lambda: fixed)

        result = eod.run_eod(trade_date="2026-08-28")

        assert result.timestamp == fixed
        assert result.trade_date == "2026-08-28"
