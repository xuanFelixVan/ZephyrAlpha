# [A_module] module_id=MOD-PRT_strategies | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Re-export wrapper: true source is zephyr.pf_core.default_equity_strategy.

Uses lazy __getattr__ to avoid double-registration in StrategyRegistry
(pf_core.strategies copy deleted; only pf_core.default_equity_strategy triggers @register).
"""

_LAZY = {
    "DefaultEquityStrategy": ("zephyr.pf_core.default_equity_strategy", "DefaultEquityStrategy"),
    "RebalanceMode": ("zephyr.pf_core.default_equity_strategy", "RebalanceMode"),
}


def __getattr__(name):
    if name in _LAZY:
        import importlib

        mod_path, attr = _LAZY[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["DefaultEquityStrategy", "RebalanceMode"]
