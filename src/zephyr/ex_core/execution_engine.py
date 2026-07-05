# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.execution_engine
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_manager; zephyr.governance.adapters.risk_validation_bridge; zephyr.trading.trading_contracts.execution.order
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
# [A_module] module_id=MOD-EXE_execution_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# ---
# domain: ex_core
# category: execution_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_EXECUTION_CORE — Execution Engine

交易执行引擎。负责订单执行、算法单（TWAP/VWAP）、经纪商智能路由（SOR）。

CTR 契约：
  消费者 — CTR-004 (Order) ← D_PORTFOLIO_CORE
  生产者 — CTR-005 (Fill) → D_REPORTING
  生产者 — CTR-006 (PositionSnapshot) → D_RISK, D_REPORTING, D_ML_TRAIN
  生产者 — CTR-ERR-005 (ExecutionRejectionError) → D_PORTFOLIO_CORE, D_REPORTING
  生产者 — CTR-P1-007 (ExecutionReport，定义见 shared.contracts) → D_REPORTING

说明：本模块内 ``ExecutionEngineRunRecord`` 为引擎内部聚合快照，非 CTR-P1-007；
跨层传输的 ExecutionReport 须使用 ``zephyr.shared.contracts.execution_report``。

SSoT: cross_layer_contracts.yaml → CTR-004 + CTR-005 + CTR-006 + CTR-P1-007
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum

from zephyr.ex_core.order_manager import OrderManager
from zephyr.governance.adapters.risk_validation_bridge import (
    RiskValidationPort,
)
from zephyr.trading.trading_contracts.execution.order import Order

_logger = logging.getLogger(__name__)


class AlgoType(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    MARKET = "market"
    TWAP = "twap"
    VWAP = "vwap"
    ICEBERG = "iceberg"


@dataclass
class ExecutionConfig:
    """执行配置"""

    default_algo: AlgoType = AlgoType.TWAP
    twap_window_minutes: int = 30
    twap_slices: int = 10
    max_slippage_bps: Decimal = Decimal("5")
    participation_rate: float = 0.10
    min_order_qty: Decimal = Decimal("100")
    round_lot: int = 100


@dataclass
class ExecutionEngineRunRecord:
    """引擎内部执行聚合记录（非 CTR-P1-007；契约类型见 shared.contracts.ExecutionReport）。"""

    report_id: str
    order_id: str
    symbol: str
    algo_type: str
    total_quantity: Decimal
    filled_quantity: Decimal
    avg_fill_price: Decimal
    target_price: Decimal
    slippage_bps: Decimal
    commission: Decimal
    start_time: datetime
    end_time: datetime
    status: str
    fills: list[dict] = field(default_factory=list)
    venue: str = "simulation"

    @property
    def fill_rate(self) -> float:
        return float(self.filled_quantity / self.total_quantity) if self.total_quantity > 0 else 0.0


class ExecutionEngine:
    """交易执行引擎——算法单执行 + SOR"""

    def __init__(
        self,
        order_manager: OrderManager,
        risk_validator: RiskValidationPort,
        config: ExecutionConfig | None = None,
    ):
        self._order_manager = order_manager
        self._config = config or ExecutionConfig()
        self._risk_validator = risk_validator
        self._algo_orders: dict[str, dict] = {}
        self._reports: dict[str, ExecutionEngineRunRecord] = {}
        self._broker_scores: dict[str, float] = defaultdict(lambda: 1.0)

    def execute_order(
        self,
        order: Order,
        algo: AlgoType | None = None,
        broker_id: str = "simulation",
    ) -> str:
        """执行单笔订单"""
        algo = algo or self._config.default_algo

        violations = self._risk_validator.validate_order(
            symbol=order.symbol,
            target_weight=float(order.quantity) / 1000000.0,
            current_holdings={},
            limits={"max_single_position": 0.10},
        )

        halt_violations = [v for v in violations if v.severity == "HALT"]
        if halt_violations:
            _logger.warning("Order rejected by risk: order_id=%s violations=%s", order.order_id, len(halt_violations))
            raise ValueError(f"Order rejected by risk validator: {halt_violations[0].description}")

        if algo is AlgoType.TWAP:
            return self._execute_twap(order, broker_id)
        elif algo is AlgoType.VWAP:
            return self._execute_vwap(order, broker_id)
        else:
            return self._execute_market(order, broker_id)

    def execute_batch(
        self,
        orders: list[Order],
        algo: AlgoType | None = None,
    ) -> list[str]:
        """批量执行订单列表"""
        broker_order_ids = []
        for order in orders:
            try:
                bid = self.execute_order(order, algo)
                broker_order_ids.append(bid)
            except ValueError as e:
                _logger.error("Order execution rejected: order_id=%s error=%s", order.order_id, e)
        return broker_order_ids

    def get_engine_run_record(self, order_id: str) -> ExecutionEngineRunRecord | None:
        return self._reports.get(order_id)

    def select_broker(self, order: Order) -> str:
        """Smart Order Router (SOR)——选择最优经纪商"""
        scored = sorted(
            self._broker_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        if scored:
            return scored[0][0]
        return "simulation"

    def update_broker_score(self, broker_id: str, fill_quality: float) -> None:
        """更新经纪商评分（基于成交质量）"""
        current = self._broker_scores[broker_id]
        self._broker_scores[broker_id] = current * 0.9 + fill_quality * 0.1

    def _execute_twap(self, order: Order, broker_id: str) -> str:
        slices = self._config.twap_slices
        broker_order_id = self._order_manager.submit_order(order.order_id, broker_id)

        self._algo_orders[order.order_id] = {
            "algo": "twap",
            "slices": slices,
            "broker_order_ids": [broker_order_id],
            "started_at": datetime.now(UTC),
        }

        return broker_order_id

    def _execute_vwap(self, order: Order, broker_id: str) -> str:
        self._algo_orders[order.order_id] = {
            "algo": "vwap",
            "started_at": datetime.now(UTC),
        }
        return self._order_manager.submit_order(order.order_id, broker_id)

    def _execute_market(self, order: Order, broker_id: str) -> str:
        return self._order_manager.submit_order(order.order_id, broker_id)


__all__ = ["AlgoType", "ExecutionConfig", "ExecutionEngine", "ExecutionEngineRunRecord"]
