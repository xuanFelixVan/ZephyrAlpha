# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.governance.escalation.result_types
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.shared.contracts.rollback_types
# [CONSUMERS] tests/governance/escalation/test_result_types;tests/governance/governance_misc/test_governance_result_types;tests/governance/governance_e2e/test_gct_003_rollback_to_escalation;tests/governance/drift/test_gct_integration;tests/governance/shared/test_phase_gates;tests/governance/security/test_p0_u1_contract_smoke
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
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md

G-CT-003 — RollbackResult backward-compat re-export facade.
Canonical home is now: zephyr.shared.contracts.rollback_types
"""

from zephyr.shared.contracts.rollback_types import (
    RollbackResult,
    RollbackStatus,
    ValidationResult,
)

__all__ = ["RollbackResult", "RollbackStatus", "ValidationResult"]
