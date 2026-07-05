# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.governance.strategies.strategy_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.strategy_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-PRT_strategy_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ==== BEGIN CODGEN:OCP-002-REGISTRY ====
# ---
# domain: pf_core
# category: ocp_extension
# status: auto_generated
# created: "2026-05-05"
# ---
"""
StrategyRegistry 卫星模块（OCP-002）

仅从 ``strategy_base`` re-export，使 ``registry_path`` 与包内 import 习惯一致。
"""

from __future__ import annotations

from .strategy_base import StrategyBase, StrategyMeta, StrategyRegistry

__all__ = ["StrategyBase", "StrategyMeta", "StrategyRegistry"]

# ==== END CODGEN:OCP-002-REGISTRY ====
