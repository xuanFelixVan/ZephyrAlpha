# [A_module] module_id=MOD-PRT_strategy_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain-pf_core/portfolio-core/blueprint.md

# [MODULE] zephyr.portfolio.core.strategy_registry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
