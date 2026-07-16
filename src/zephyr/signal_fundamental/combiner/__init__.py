# [A_module] module_id=MOD-UNK_combiner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
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
    SignalAggregatorBase,
)
from zephyr.signal_fundamental.strategy.capital_allocator import (
    CapitalAllocationResult,
    CapitalAllocatorBase,
)
from zephyr.signal_fundamental.synth.signal_synthesizer import SignalSynthesizerBase
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal

# DegradationMonitorBase 真源已迁移至 D_SIGQC 域（2026-07-06 域边界修正）。
# 通过 __getattr__ 跨域 re-export 向后兼容，避免直接 import 已迁移的符号导致 ImportError。


def __getattr__(name):
    if name == "DegradationMonitorBase":
        from zephyr.signal_quality.degradation_monitor_base import DegradationMonitorBase

        return DegradationMonitorBase
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
]
