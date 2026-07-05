# [BLUEPRINT] SRC-195 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.pf_alloc.strategy_lifecycle_event
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.shared.contracts.portfolio.strategy_lifecycle_event
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_strategy_lifecycle_event | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export from shared SSoT — zephyr.shared.contracts.portfolio.strategy_lifecycle_event
from zephyr.shared.contracts.portfolio.strategy_lifecycle_event import StrategyLifecycleEvent

__all__ = ["StrategyLifecycleEvent"]
