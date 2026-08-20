# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] tests.ex_core.test_execution_report
# [DOMAIN] D_EX_CORE
# [INVARIANTS] CTR-P1-007契约产出; 滑点带方向符号(正=不利); 输入不一致Fail-Closed
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidExecutionReportInputError
# [TESTS] self
# [TTL] permanent
"""CTR-P1-007 ExecutionReport 产出逻辑测试（GAP-L06-003，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from zephyr.ex_core.execution_engine import ExecutionEngineRunRecord
from zephyr.ex_core.execution_report import (
    InvalidExecutionReportInputError,
    build_execution_report,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.execution_report import ExecutionReport
from zephyr.shared.contracts.order import Order


def _order(side: OrderSide = OrderSide.BUY, qty: str = "1000", limit: str = "10.00") -> Order:
    return Order(
        idempotency_key="idem-o1",
        order_id="o1",
        order_type=OrderType.LIMIT,
        quantity=Decimal(qty),
        side=side,
        strategy_id="S1",
        symbol="600000",
        limit_price=Decimal(limit),
        created_at=datetime(2026, 8, 20, 10, 0, tzinfo=UTC),
    )


def _record(
    filled: str = "1000",
    avg: str = "10.02",
    total: str = "1000",
    target: str = "10.00",
    order_id: str = "o1",
) -> ExecutionEngineRunRecord:
    return ExecutionEngineRunRecord(
        report_id="rpt-b1",
        order_id=order_id,
        symbol="600000",
        algo_type="TWAP",
        total_quantity=Decimal(total),
        filled_quantity=Decimal(filled),
        avg_fill_price=Decimal(avg),
        target_price=Decimal(target),
        slippage_bps=Decimal("0"),
        commission=Decimal("5.25"),
        start_time=datetime(2026, 8, 20, 10, 0, 0, tzinfo=UTC),
        end_time=datetime(2026, 8, 20, 10, 5, 0, tzinfo=UTC),
        status="FILLED",
        venue="miniqmt",
    )


class TestBuildExecutionReport:
    def test_happy_path_full_contract(self):
        report = build_execution_report(_order(), _record())
        assert isinstance(report, ExecutionReport)
        assert report.order_id == "o1"
        assert report.symbol == "600000"
        assert report.direction == OrderSide.BUY.value
        assert report.broker_id == "miniqmt"
        assert report.algo_type == "TWAP"
        assert report.intended_quantity == 1000
        assert report.actual_quantity == 1000
        assert report.intended_price == Decimal("10.00")
        assert report.vwap_price == Decimal("10.02")
        assert report.commission == Decimal("5.25")
        assert report.idempotency_key == "idem-o1"
        assert report.execution_start == "2026-08-20T10:00:00+00:00"
        assert report.execution_end == "2026-08-20T10:05:00+00:00"

    def test_buy_adverse_slippage_positive(self):
        # 买贵：10.02 vs 10.00 → +20bps（不利）
        report = build_execution_report(_order(side=OrderSide.BUY), _record(avg="10.02"))
        assert report.slippage_bps == pytest.approx(20.0)

    def test_buy_favorable_slippage_negative(self):
        report = build_execution_report(_order(side=OrderSide.BUY), _record(avg="9.99"))
        assert report.slippage_bps == pytest.approx(-10.0)

    def test_sell_adverse_slippage_positive(self):
        # 卖贱：9.98 vs 10.00 → +20bps（不利，方向符号翻转）
        report = build_execution_report(_order(side=OrderSide.SELL), _record(avg="9.98"))
        assert report.slippage_bps == pytest.approx(20.0)

    def test_zero_intended_price_slippage_degrades_zero(self):
        order = _order(limit="10.00")
        report = build_execution_report(order, _record(target="0", avg="0"))
        assert report.slippage_bps == 0.0

    def test_partial_fill_quantities(self):
        report = build_execution_report(_order(), _record(filled="600"))
        assert report.actual_quantity == 600
        assert report.intended_quantity == 1000

    def test_order_id_mismatch_rejected(self):
        with pytest.raises(InvalidExecutionReportInputError):
            build_execution_report(_order(), _record(order_id="o2"))

    def test_non_positive_intended_quantity_rejected(self):
        with pytest.raises(InvalidExecutionReportInputError):
            build_execution_report(_order(), _record(total="0"))

    def test_negative_filled_rejected(self):
        with pytest.raises(InvalidExecutionReportInputError):
            build_execution_report(_order(), _record(filled="-1"))

    def test_negative_price_rejected(self):
        with pytest.raises(InvalidExecutionReportInputError):
            build_execution_report(_order(), _record(avg="-0.01"))
