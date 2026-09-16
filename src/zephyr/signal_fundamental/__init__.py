# [A_module] module_id=MOD-L03-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""

D_SIGNAL Signal Domain

Signal域统一包。聚合信号生成、策略、合成、组合、资本配置和管线。

子模块:
  gen/       — 信号生成 (SignalAggregatorBase, CapitalAllocatorBase)
  strategy/  — 资本配置策略 (CapitalAllocatorBase re-export, DefaultCapitalAllocator)
  synth/     — 信号合成 (SignalSynthesizerBase)
  combiner/  — 信号合成组合器 (SynthesizedSignal)
  capital/   — 多策略资本配置 (CapitalAllocationResult, DefaultCapitalAllocator)
  pipeline.py — Alpha信号管线 (AlphaSignalPipeline)

# [ALGO_FLOW] external: docs/03_modules/_domain_fundamental_signal/algo_flow/signal_fundamental__init__.yaml
"""

from __future__ import annotations
from zephyr.signal_fundamental.pead_event_model import PeadEventModel

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
        # DegradationMonitorBase 真源已迁移至 D_SIGQC 域（2026-07-06 域边界修正）。
        "DegradationMonitorBase": "zephyr.signal_quality.degradation_monitor_base",
        "SignalSynthesizerBase": ".synth.signal_synthesizer",
        "AlphaSignalPipeline": ".pipeline",
        # SynthesizedSignal 真源在 shared/contracts（CTR-P1-015 契约 SSoT），
        # combiner/synthesized_signal.py 不存在——原指向悬空模块会 ModuleNotFoundError。
        "SynthesizedSignal": "zephyr.shared.contracts.synthesized_signal",
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


__all__.append("PeadEventModel")

# ORPHAN-MODULE: 引用登记（gw-tdm-20260909：C7 负面否决器）
from zephyr.signal_fundamental.negative_veto import apply_negative_veto  # noqa: F401
