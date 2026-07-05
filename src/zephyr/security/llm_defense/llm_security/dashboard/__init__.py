# [A_module] module_id=MOD-SEC_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [TTL] permanent
"""LLM Security Gateway Dashboard Module.

Uses lazy __getattr__ for app submodule to avoid hard dependency on
plotly/streamlit at package import time (dashboard is an optional component).
"""


def __getattr__(name):
    if name == "app":
        import importlib

        mod = importlib.import_module(f"{__name__}.app")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["app"]
