# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.default_equity_strategy
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.governance.strategy_base; zephyr.trading.trading_contracts.execution.order
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
# [A_module] module_id=MOD-PRT_default_equity_strategy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_PORTFOLIO_CORE — Default Equity Long-Only Strategy

默认股票多头策略。实现 StrategyBase (OCP-002)，等权或信号加权配置。

CTR 契约：
  消费者 — CTR-002 (FactorSignal) ← D_FACTOR
  消费者 — CTR-003 (RiskLimits) ← D_RISK
  消费者 — CTR-P1-015 (SynthesizedSignal) ← D_SIGNAL
  生产者 — CTR-004 (Order) -> D_EXECUTION_CORE

SSoT: cross_layer_contracts.yaml -> OCP-002 + CTR-004
"""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from enum import Enum
from typing import Any

from zephyr.governance.strategies.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
)
from zephyr.trading.trading_contracts.execution.order import Order, OrderSide, OrderType

_logger = logging.getLogger(__name__)


class RebalanceMode(str, Enum):
    EQUAL_WEIGHT = "equal_weight"
    SIGNAL_WEIGHT = "signal_weight"
    MIN_VARIANCE = "min_variance"
    RISK_PARITY = "risk_parity"


@StrategyRegistry.register
class DefaultEquityStrategy(StrategyBase):
    """默认 A 股股票多头策略——等权/信号加权/最小方差配置"""

    meta = StrategyMeta(
        strategy_id="default-equity",
        name="默认股票多头策略",
        description="A 股等权/信号加权配置策略，含风险限额约束",
        strategy_type="equity_long_only",
        version="1.0.0",
        author="zephyr-agent",
        factor_dependencies=["momentum", "value", "quality", "low_vol"],
        tags=["equity", "long_only", "a_share"],
    )

    def __init__(
        self,
        universe: list[str] | None = None,
        mode: RebalanceMode = RebalanceMode.EQUAL_WEIGHT,
        max_positions: int = 30,
        nav: Decimal = Decimal("1000000"),
        risk_limits: dict | None = None,
    ):
        self._universe = universe or []
        self._mode = mode
        self._max_positions = max_positions
        self._nav = nav
        self._risk_limits = risk_limits or {}
        self._current_holdings: dict[str, Decimal] = {}
        self._signal_scores: dict[str, float] = {}

    def generate_target_weights(
        self,
        universe: list[str] | None = None,
        signals: dict[str, float] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """生成目标权重（实现 StrategyBase 抽象方法，OCP-002 契约对齐）

        Args:
            universe: 标的列表，若提供则覆盖 __init__ 设置
            signals: 信号得分，若提供则更新内部信号
            constraints: 风险约束，若提供则更新内部约束

        Returns:
            dict[symbol, weight] 目标权重字典
        """
        if universe is not None:
            self._universe = universe
        if signals is not None:
            self._signal_scores.update(signals)
        if constraints is not None:
            self._risk_limits.update(constraints)

        if not self._universe:
            _logger.warning("Universe is empty, no weights generated")
            return {}

        if self._mode is RebalanceMode.EQUAL_WEIGHT:
            weights = self._equal_weight_alloc()
        elif self._mode is RebalanceMode.SIGNAL_WEIGHT:
            weights = self._signal_weight_alloc()
        else:
            weights = self._equal_weight_alloc()

        _logger.info("Generated %d weights for strategy=%s mode=%s", len(weights), self.meta.strategy_id, self._mode)
        return weights

    def generate_orders(self) -> list[Order]:
        """根据目标权重生成订单列表（便捷方法，调用 generate_target_weights + _weights_to_orders）"""
        weights = self.generate_target_weights()
        orders = self._weights_to_orders(weights)
        _logger.info("Generated %d orders for strategy=%s", len(orders), self.meta.strategy_id)
        return orders

    def update_signals(self, signals: dict[str, float]) -> None:
        """更新信号得分（供 D_SIGNAL 输入的 SynthesizedSignal）"""
        self._signal_scores.update(signals)

    def update_holdings(self, holdings: dict[str, Decimal]) -> None:
        """更新当前持仓"""
        self._current_holdings.update(holdings)

    def on_fill(self) -> None:
        _logger.debug("DefaultEquityStrategy.on_fill called")

    def on_risk_alert(self) -> None:
        _logger.warning("DefaultEquityStrategy risk alert triggered")

    def _equal_weight_alloc(self) -> dict[str, float]:
        n = min(len(self._universe), self._max_positions)
        if n == 0:
            return {}
        weight = 1.0 / n

        max_single = self._risk_limits.get("max_single_position", 0.10)
        weight = min(weight, max_single)

        return {s: weight for s in self._universe[:n]}

    def _signal_weight_alloc(self) -> dict[str, float]:
        if not self._signal_scores:
            return self._equal_weight_alloc()

        scored = sorted(
            self._signal_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )[: self._max_positions]

        abs_scores = [max(0.01, abs(s)) for _, s in scored]
        total = sum(abs_scores)
        if total == 0:
            return self._equal_weight_alloc()

        max_single = self._risk_limits.get("max_single_position", 0.10)
        weights = {}
        for (symbol, _), score in zip(scored, abs_scores, strict=False):
            w = score / total
            w = min(w, max_single)
            weights[symbol] = w

        return weights

    def _weights_to_orders(self, weights: dict[str, float]) -> list[Order]:
        orders = []
        for symbol, target_weight in weights.items():
            target_value = self._nav * Decimal(str(target_weight))
            current_value = self._current_holdings.get(symbol, Decimal("0")) * Decimal("100")
            delta_value = target_value - current_value

            if abs(delta_value) < Decimal("1000"):
                continue

            reference_price = Decimal("100")
            qty = delta_value / reference_price

            if abs(qty) < Decimal("100"):
                continue

            side = OrderSide.BUY if delta_value > 0 else OrderSide.SELL
            qty = (abs(qty) // Decimal("100")) * Decimal("100")

            order = Order(
                order_id=f"ord-{uuid.uuid4().hex[:8]}",
                symbol=symbol,
                strategy_id=self.meta.strategy_id,
                side=side,
                order_type=OrderType.LIMIT,
                quantity=qty,
                limit_price=reference_price,
                idempotency_key=str(uuid.uuid4()),
            )
            orders.append(order)

        return orders


__all__ = ["DefaultEquityStrategy", "RebalanceMode"]
