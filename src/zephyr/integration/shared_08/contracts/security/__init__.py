# [A_module] module_id=MOD-SEC_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-185 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.security
# [INVARIANTS] SecurityDecision enum values are frozen; no additions without KBG decision
# [MODIFY-GUARD] enum member changes require cross-package impact review
# [CONSUMERS] infrastructure_runtime_integration; l10-compliance; llm-security
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] tests/test_shared_contracts_security.py

__all__ = [
    "SecurityDecision",
    "security_decision",
]
