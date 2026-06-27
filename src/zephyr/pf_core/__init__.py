# [A_module] module_id=MOD-PRT_pf_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain-pf_core/portfolio-core/blueprint.md
# [MODULE] zephyr.pf_core
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""L05 Portfolio Construction — Re-export wrapper (DM-298)

All modules have been migrated to zephyr.portfolio_core.core.
This package re-exports for backward compatibility.
"""

from __future__ import annotations

__all__ = [
    "AttributionEngineBase",
    "ComplianceRule",
    "DefaultAttributionEngine",
    "DefaultEquityStrategy",
    "DefaultTCAEngine",
    "PerformanceAttributionReport",
    "RebalanceMode",
    "RiskLimits",
    "StrategyBase",
    "StrategyMeta",
    "StrategyRegistry",
    "TCAEngineBase",
    "analytics_base",
    "autodiscover_strategies",
    "compliance_rule",
    "default_attribution_engine",
    "default_equity_strategy",
    "default_tca_engine",
    "performance_attribution_report",
    "risk_limits",
    "strategy_base",
    "strategy_registry",
]

_LAZY_IMPORTS = {
    "StrategyBase": ("zephyr.pf_core.strategy_base", "StrategyBase"),
    "StrategyMeta": ("zephyr.pf_core.strategy_base", "StrategyMeta"),
    "StrategyRegistry": ("zephyr.pf_core.strategy_base", "StrategyRegistry"),
    "autodiscover_strategies": ("zephyr.pf_core.strategy_base", "autodiscover_strategies"),
    "DefaultEquityStrategy": ("zephyr.pf_core.default_equity_strategy", "DefaultEquityStrategy"),
    "RebalanceMode": ("zephyr.pf_core.default_equity_strategy", "RebalanceMode"),
    "ComplianceRule": ("zephyr.pf_core.compliance_rule", "ComplianceRule"),
    "PerformanceAttributionReport": ("zephyr.pf_core.performance_attribution_report", "PerformanceAttributionReport"),
    "TCAEngineBase": ("zephyr.pf_core.analytics_base", "TCAEngineBase"),
    "AttributionEngineBase": ("zephyr.pf_core.analytics_base", "AttributionEngineBase"),
    "DefaultAttributionEngine": ("zephyr.pf_core.default_attribution_engine", "DefaultAttributionEngine"),
    "DefaultTCAEngine": ("zephyr.pf_core.default_tca_engine", "DefaultTCAEngine"),
    "RiskLimits": ("zephyr.pf_core.risk_limits", "RiskLimits"),
}

_SUBMODULES = [
    "analytics_base",
    "default_attribution_engine",
    "default_tca_engine",
    "risk_limits",
    "strategy_registry",
    "compliance_rule",
    "default_equity_strategy",
    "performance_attribution_report",
    "strategy_base",
]


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        import importlib

        mod_path, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_path)
        value = getattr(mod, attr_name)
        globals()[name] = value
        return value
    if name in _SUBMODULES:
        import importlib

        mod = importlib.import_module(f"zephyr.pf_core.{name}")
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
