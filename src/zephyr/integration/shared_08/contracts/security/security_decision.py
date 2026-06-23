# [BLUEPRINT] SRC-186 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.security.security_decision
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] orchestration.agent_communication; l10-compliance; llm-security.protocol
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] enum members are frozen; no additions without KBG decision
# [MODIFY-GUARD] member changes require cross-package impact review
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] tests/test_shared_contracts_security.py
# [A_module] module_id=MOD-SEC_security_decision | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from enum import Enum


class SecurityDecision(Enum):
    BLOCK = "block"
    ALLOW = "allow"
    DENY = "deny"
    FLAG = "flag"
