# [A_module] module_id=MOD-SEC_security_decision | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.security.security_decision
# [INVARIANTS] enum members are frozen; no additions without ADR
# [MODIFY-GUARD] member changes require cross-package impact review
# [CONSUMERS] orchestration.agent_communication; l10-compliance; llm-security.protocol
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] tests/test_shared_contracts_security.py

from enum import Enum


class SecurityDecision(Enum):
    BLOCK = "block"
    ALLOW = "allow"
    DENY = "deny"
    FLAG = "flag"
