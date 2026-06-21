# [A_module] module_id=MOD-UNK_strategy_lifecycle_event | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] SRC-195 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md

# [MODULE] zephyr.portfolio.allocation.strategy_lifecycle_event

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT]

# [TESTS]

# Re-export from shared SSoT — zephyr.shared.contracts.portfolio.strategy_lifecycle_event
from zephyr.shared.contracts.portfolio.strategy_lifecycle_event import StrategyLifecycleEvent  # noqa: F401

__all__ = ["StrategyLifecycleEvent"]
