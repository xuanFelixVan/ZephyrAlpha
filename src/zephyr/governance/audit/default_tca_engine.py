# [BLUEPRINT] MOD-L07-001 | docs/03_modules/_domain_reporting/blueprint.md
# [MODULE] zephyr.governance.audit.default_tca_engine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.reporting.analytics_base; zephyr.trading.trading_contracts.execution.execution_report; zephyr.trading.trading_contracts.execution.fill; zephyr.trading.trading_contracts.execution.order
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_default_tca_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: reporting
# category: analytics_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_REPORTING — Default TCA Engine

交易成本分析引擎具体实现。成交回报 → 执行分析报告。

CTR 契约：
  消费者 — CTR-005 (Fill) ← D_EXECUTION_CORE
  消费者 — CTR-004 (Order) ← D_PORTFOLIO_CORE（关联委托）
  生产者 — CTR-P1-007 (ExecutionReport) → D_FRONTEND, D_COMPLIANCE

SSoT: cross_layer_contracts.yaml → CTR-005 + CTR-P1-007
"""

from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_EVEN

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
            # 5.105.4 修复: int(Decimal) 向零截断而非四舍五入,执行报告数量被低估
            # 改用 to_integral_value(rounding=ROUND_HALF_EVEN) 银行家舍入
            intended_quantity=int(order.quantity.to_integral_value(rounding=ROUND_HALF_EVEN)),
            actual_quantity=int(fill.filled_quantity.to_integral_value(rounding=ROUND_HALF_EVEN)),
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
