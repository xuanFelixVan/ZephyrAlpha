# [A_module] module_id=MOD-UNK_combiner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain-signal/signal-generation-core/blueprint.md
# [MODULE] zephyr.signal_fundamental.combiner
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_SIGNAL Signal Combiner

信号合成组合器。聚合信号生成、策略、合成为统一入口。
"""

from __future__ import annotations

from zephyr.signal_fundamental.gen.aggregator_base import (
    DegradationMonitorBase,
    SignalAggregatorBase,
)
from zephyr.signal_fundamental.strategy.capital_allocator import (
    CapitalAllocationResult,
    CapitalAllocatorBase,
)
from zephyr.signal_fundamental.synth.signal_synthesizer import SignalSynthesizerBase
from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal

__all__ = [
    "CapitalAllocationResult",
    "CapitalAllocatorBase",
    "DegradationMonitorBase",
    "SignalAggregatorBase",
    "SignalSynthesizerBase",
    "SynthesizedSignal",
    "aggregator_base",
    "capital_allocator",
    "signal_synthesizer",
    "synthesized_signal",
]
