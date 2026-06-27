# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.governance.result_types
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.rollback_types
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
# [A_module] module_id=MOD-GOV_result_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""G-CT-003 — RollbackResult backward-compat re-export facade.
Canonical home is now: zephyr.integration.shared_08.contracts.rollback_types
"""

from zephyr.integration.shared_08.contracts.rollback_types import (
    RollbackResult,
    RollbackStatus,
    ValidationResult,
)

__all__ = ["RollbackResult", "RollbackStatus", "ValidationResult"]
