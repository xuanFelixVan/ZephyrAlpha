# [A_module] module_id=MOD-PRT-pf_core | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core
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

D_PORTFOLIO_CORE Portfolio Construction — Package root

# [ALGO_FLOW] external: docs/03_modules/_domain_portfolio_core/algo_flow/pf_core__init__.yaml
"""

from __future__ import annotations

__all__ = [
    "ComplianceRule",
    "DefaultEquityStrategy",
    "PerformanceAttributionReport",
    "RebalanceMode",
    "RiskLimits",
    "StrategyBase",
    "StrategyMeta",
    "StrategyRegistry",
    "autodiscover_strategies",
    "compliance_rule",
    "default_equity_strategy",
    "performance_attribution_report",
    "strategy_base",
    "strategy_registry",
]

_LAZY_IMPORTS = {
    # ARCH-GOV-SHIM-001 阶段3：pf_core strategy_base/compliance_rule shim 已删除，直接指向 canonical 路径
    "StrategyBase": ("zephyr.governance.strategies.strategy_base", "StrategyBase"),
    "StrategyMeta": ("zephyr.governance.strategies.strategy_base", "StrategyMeta"),
    "StrategyRegistry": ("zephyr.governance.strategies.strategy_base", "StrategyRegistry"),
    "autodiscover_strategies": ("zephyr.governance.strategies.strategy_base", "autodiscover_strategies"),
    "DefaultEquityStrategy": ("zephyr.pf_core.default_equity_strategy", "DefaultEquityStrategy"),
    "RebalanceMode": ("zephyr.pf_core.default_equity_strategy", "RebalanceMode"),
    "ComplianceRule": ("zephyr.shared.contracts.compliance_rule", "ComplianceRule"),
    "PerformanceAttributionReport": (
        "zephyr.shared.contracts.performance_attribution_report",
        "PerformanceAttributionReport",
    ),
    # ARCH-GOV-SHIM-001 阶段2：RiskLimits 直接指向 canonical 路径（原 pf_core.risk_limits shim 已删除）
    # 2026-08-17 修正：canonical 以 cross_layer_contracts.yaml CTR-003 physical_path 为准
    # （src/zephyr/shared/contracts/risk_limits.py），与 pf_core 核心模块实际 import 真源一致
    "RiskLimits": ("zephyr.shared.contracts.risk_limits", "RiskLimits"),
}

# ARCH-GOV-SHIM-001 阶段3：_SUBMODULES 改为 dict 映射 canonical 路径（原 pf_core shim 已删除）
_SUBMODULES = {
    "strategy_registry": "zephyr.governance.strategies.strategy_base",
    "compliance_rule": "zephyr.shared.contracts.compliance_rule",
    "default_equity_strategy": "zephyr.pf_core.default_equity_strategy",
    # 2026-08-17 修正：原指向已删除的 pf_core shim（ModuleNotFoundError），
    # canonical=shared.contracts（cross_layer_contracts.yaml CTR-P1-009 physical_path）
    "performance_attribution_report": "zephyr.shared.contracts.performance_attribution_report",
    "strategy_base": "zephyr.governance.strategies.strategy_base",
}


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

        mod = importlib.import_module(_SUBMODULES[name])
        globals()[name] = mod
        return mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# ORPHAN-MODULE: 引用登记（让 depgraph 发现 import 边）
from zephyr.pf_core.strategy_correlation_pipeline import run_strategy_correlation_pipeline  # noqa: F401
