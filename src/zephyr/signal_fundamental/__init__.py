# [A_module] module_id=MOD-UNK_signal | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain-signal/signal-generation-core/blueprint.md
# [MODULE] zephyr.signal_fundamental
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_SIGNAL Signal Domain

Signal域统一包。聚合信号生成、策略、合成、组合、资本配置和管线。

子模块:
  gen/       — 信号生成 (SignalAggregatorBase, CapitalAllocatorBase, DegradationMonitorBase)
  strategy/  — 资本配置策略 (CapitalAllocatorBase re-export, DefaultCapitalAllocator)
  synth/     — 信号合成 (SignalSynthesizerBase)
  combiner/  — 信号合成组合器 (SynthesizedSignal)
  capital/   — 多策略资本配置 (CapitalAllocationResult, DefaultCapitalAllocator)
  pipeline/  — Alpha信号管线 (AlphaSignalPipeline)
"""

from __future__ import annotations

__all__ = [
    "AllocationMethod",
    "AlphaSignalPipeline",
    "CapitalAllocationResult",
    "CapitalAllocatorBase",
    "DefaultCapitalAllocator",
    "DefaultSignalAggregator",
    "DegradationMonitorBase",
    "SignalAggregatorBase",
    "SignalSynthesizerBase",
    "SynthesizedSignal",
    "pipeline",
]


def __getattr__(name):
    _lazy = {
        "SignalAggregatorBase": ".gen.aggregator_base",
        "CapitalAllocatorBase": ".gen.aggregator_base",
        "DegradationMonitorBase": ".gen.aggregator_base",
        "SignalSynthesizerBase": ".synth.signal_synthesizer",
        "AlphaSignalPipeline": ".pipeline",
        "SynthesizedSignal": ".combiner.synthesized_signal",
        "CapitalAllocationResult": ".capital.capital_allocation_result",
        "DefaultSignalAggregator": ".gen.implementations.default_signal_aggregator",
        "DefaultCapitalAllocator": ".strategy.implementations.default_capital_allocator",
        "AllocationMethod": ".strategy.implementations.default_capital_allocator",
    }
    if name in _lazy:
        import importlib

        mod = importlib.import_module(_lazy[name], __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
