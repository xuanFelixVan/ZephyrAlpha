# [A_module] module_id=MOD-SEC_security_contracts_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.contracts.security
# [INVARIANTS] SecurityDecision enum values are frozen; no additions without ADR
# [MODIFY-GUARD] enum member changes require cross-package impact review
# [CONSUMERS] infrastructure_runtime_integration; l10-compliance; llm-security
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] tests/test_shared_contracts_security.py
# [TTL] permanent

__all__ = [
    "SecurityDecision",
    "security_decision",
]

from zephyr.shared.contracts.security.security_decision import SecurityDecision
