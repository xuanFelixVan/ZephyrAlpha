# [A_module] module_id=MOD-PRT_default_tca_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain-reporting/analytics-core/blueprint.md

# [MODULE] zephyr.portfolio.core.default_tca_engine

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

# ---
# domain: reporting
# category: analytics_implementation
# status: active
# created: "2026-05-05"
# ---

"""L07 — Default TCA Engine

交易成本分析引擎具体实现。成交回报 → 执行分析报告。

CTR 契约：
  消费者 — CTR-005 (Fill) ← L06
  消费者 — CTR-004 (Order) ← L05（关联委托）
  生产者 — CTR-P1-007 (ExecutionReport) → L08, L10

SSoT: cross_layer_contracts.yaml → CTR-005 + CTR-P1-007
"""

from __future__ import annotations

import logging
from decimal import Decimal

from zephyr.reporting.analytics_base import TCAEngineBase
from zephyr.trading.trading_contracts.execution.execution_report import ExecutionReport
from zephyr.trading.trading_contracts.execution.fill import Fill
from zephyr.trading.trading_contracts.execution.order import Order

_logger = logging.getLogger(__name__)

__tca_id__ = "default-tca-engine"


class DefaultTCAEngine(TCAEngineBase):
    """默认 TCA 引擎——滑点/佣金/冲击成本分析"""

    __tca_id__ = __tca_id__

    def __init__(self, benchmark_price_source: str = "arrival"):
        self._benchmark_source = benchmark_price_source

    def analyze(self, fill: Fill, order: Order, idempotency_key: str) -> ExecutionReport:
        intended_price = order.limit_price or Decimal("100")
        fill_price = fill.fill_price

        slippage_bps = Decimal("0")
        if intended_price > 0:
            slippage_bps = (fill_price - intended_price) / intended_price * Decimal("10000")

        commission = fill.commission or Decimal("0")

        direction = "BUY" if (order.side and order.side.name == "BUY") else "SELL"

        return ExecutionReport(
            order_id=order.order_id,
            symbol=fill.symbol,
            direction=direction,
            intended_quantity=int(order.quantity),
            actual_quantity=int(fill.filled_quantity),
            intended_price=intended_price,
            vwap_price=fill.fill_price,
            slippage_bps=float(slippage_bps),
            commission=commission,
            execution_start=fill.fill_timestamp.isoformat() if fill.fill_timestamp else "",
            execution_end=fill.fill_timestamp.isoformat() if fill.fill_timestamp else "",
            broker_id=fill.broker_fill_id or "unknown",
            idempotency_key=idempotency_key,
        )

    def analyze_batch(
        self,
        fills: list[Fill],
        orders: dict[str, Order],
        idempotency_key: str,
    ) -> list[ExecutionReport]:
        reports = []
        for fill in fills:
            order = orders.get(fill.order_id)
            if order:
                report = self.analyze(fill, order, idempotency_key)
                reports.append(report)
        _logger.info("Batch TCA: %d fills → %d reports", len(fills), len(reports))
        return reports

    def _calc_shortfall(self, fill: Fill, order: Order) -> Decimal:
        """计算 Implementation Shortfall"""
        decision_price = order.limit_price or Decimal("0")
        if decision_price == 0:
            return Decimal("0")

        fill_value = fill.filled_quantity * fill.fill_price
        paper_value = fill.filled_quantity * decision_price

        return (paper_value - fill_value - (fill.commission or Decimal("0"))) / paper_value


__all__ = ["DefaultTCAEngine"]
