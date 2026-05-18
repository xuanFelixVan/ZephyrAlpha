# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.security.security_decision
# [INVARIANTS] enum members are frozen; no additions without ADR
# [MODIFY-GUARD] member changes require cross-package impact review
# [CONSUMERS] l01_infrastructure.a2a_protocol; l10_compliance; llm_security.protocol
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
