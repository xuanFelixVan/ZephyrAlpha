# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.result_types
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.integration.shared_08.contracts.rollback_types
# [CONSUMERS] rollback_executor;rollback_verifier;auto_rollback_trigger
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 结果类型定义;不可随意扩展
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RollbackError;TypeError
# [TESTS] tests/rollback/
# [A_module] module_id=MOD-RES_result_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md

G-CT-003 — RollbackResult backward-compat re-export facade.
Canonical home is now: zephyr.integration.shared_08.contracts.rollback_types
"""

from zephyr.integration.shared_08.contracts.rollback_types import (
    RollbackResult,
    RollbackStatus,
    ValidationResult,
)

__all__ = ["RollbackResult", "RollbackStatus", "ValidationResult"]
