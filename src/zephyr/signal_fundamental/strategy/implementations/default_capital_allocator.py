# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.strategy.implementations.default_capital_allocator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.gen.aggregator_base; zephyr.trading.trading_contracts.execution.capital_allocation_result; zephyr.trading.trading_contracts.market.synthesized_signal
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_default_capital_allocator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal
# category: allocation_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_SIGNAL — Default Capital Allocator

资本分配器具体实现。合成信号 -> 资本配置权重。

CTR 契约：
  消费者 — CTR-P1-015 (SynthesizedSignal) ← 本层
  生产者 — CTR-P1-003 (CapitalAllocationResult) -> D_PORTFOLIO_CORE

SSoT: cross_layer_contracts.yaml -> CTR-P1-003 + CTR-P1-015
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import Enum

from zephyr.signal_fundamental.gen.aggregator_base import CapitalAllocatorBase
from zephyr.trading.trading_contracts.execution.capital_allocation_result import CapitalAllocationResult
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal

_logger = logging.getLogger(__name__)

__allocator_id__ = "default-capital-allocator"


class AllocationMethod(str, Enum):
    EQUAL = "equal_weight"
    SIGNAL = "signal_weight"
    SHARPE = "sharpe_weight"
    RISK_PARITY = "risk_parity"


class DefaultCapitalAllocator(CapitalAllocatorBase):
    """默认资本分配器——四种分配策略"""

    __allocator_id__ = __allocator_id__

    def __init__(
        self,
        method: AllocationMethod = AllocationMethod.EQUAL,
        min_signal_threshold: float = 0.2,
        max_per_strategy: float = 0.40,
    ):
        self._method = method
        self._min_signal_threshold = min_signal_threshold
        self._max_per_strategy = max_per_strategy

    def allocate(
        self,
        signals: list[SynthesizedSignal],
        idempotency_key: str,
    ) -> CapitalAllocationResult:
        if not signals:
            return self._empty_allocation(idempotency_key)

        valid = [s for s in signals if abs(s.signal_value) > self._min_signal_threshold]
        n = len(valid)

        if self._method is AllocationMethod.EQUAL:
            weights = self._equal_alloc(valid, n)
        elif self._method is AllocationMethod.SIGNAL:
            weights = self._signal_alloc(valid)
        elif self._method is AllocationMethod.SHARPE:
            weights = self._sharpe_alloc(valid, n)
        elif self._method is AllocationMethod.RISK_PARITY:
            weights = self._risk_parity_alloc(valid, n)
        else:
            weights = self._equal_alloc(valid, n)

        strategy_allocations = {s.signal_id: w for s, w in zip(valid, weights, strict=False)}
        total_allocated = sum(strategy_allocations.values())

        return CapitalAllocationResult(
            allocation_date=datetime.now(UTC).strftime("%Y-%m-%d"),
            total_allocated_weight=total_allocated,
            allocation_method=self._method,
            idempotency_key=idempotency_key,
            strategy_allocations=strategy_allocations,
        )

    def _equal_alloc(self, signals: list[SynthesizedSignal], n: int) -> list[float]:
        base = 1.0 / n if n > 0 else 0
        return [min(base, self._max_per_strategy)] * n

    def _signal_alloc(self, signals: list[SynthesizedSignal]) -> list[float]:
        abs_signals = [abs(s.signal_value) for s in signals]
        total = sum(abs_signals)
        if total == 0:
            return [1.0 / len(signals)] * len(signals)
        return [min(abs_s / total, self._max_per_strategy) for abs_s in abs_signals]

    def _sharpe_alloc(self, signals: list[SynthesizedSignal], n: int) -> list[float]:
        scores = [s.confidence or 0.5 for s in signals]
        total = sum(scores)
        if total == 0:
            return self._equal_alloc(signals, n)
        return [min(sc / total, self._max_per_strategy) for sc in scores]

    def _risk_parity_alloc(self, signals: list[SynthesizedSignal], n: int) -> list[float]:
        volatilities = [max(abs(s.signal_value / 3.0), 0.05) for s in signals]
        inv_vols = [1.0 / v for v in volatilities]
        total = sum(inv_vols)
        if total == 0:
            return self._equal_alloc(signals, n)
        return [min(iv / total, self._max_per_strategy) for iv in inv_vols]

    def _empty_allocation(self, idempotency_key: str) -> CapitalAllocationResult:
        return CapitalAllocationResult(
            allocation_date=datetime.now(UTC).strftime("%Y-%m-%d"),
            total_allocated_weight=0.0,
            allocation_method=self._method,
            idempotency_key=idempotency_key,
            strategy_allocations={},
        )


__all__ = ["AllocationMethod", "DefaultCapitalAllocator"]
