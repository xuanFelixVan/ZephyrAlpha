# [A_module] module_id=MOD-UNK_gen | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain-signal/signal-generation-core/blueprint.md
# [MODULE] zephyr.signal_fundamental.gen
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""Signal Generation sub-package"""

from __future__ import annotations

__all__ = [
    "CapitalAllocatorBase",
    "DegradationMonitorBase",
    "SignalAggregatorBase",
    "aggregator_base",
]


def __getattr__(name):
    _lazy = {
        "SignalAggregatorBase": ".aggregator_base",
        "CapitalAllocatorBase": ".aggregator_base",
        "DegradationMonitorBase": ".aggregator_base",
    }
    if name in _lazy:
        import importlib

        mod = importlib.import_module(_lazy[name], __name__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
