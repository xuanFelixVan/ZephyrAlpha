# [BLUEPRINT] MOD-SECURITY
# [MODULE] zephyr.security.access_control.capability_check
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests.test_capability_check; tests.test_governance_capability_check; tests.governance.test_adversarial_contract_attacks; tests.governance.test_gct_integration; tests.governance.test_p0_u1_contract_smoke; tests.governance.test_p0_u2_input_validation
# [STARTUP] imported
# [MATURITY] stub
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Stub module: zephyr.security.access_control.capability_check — implementation pending."""

from typing import Final

MAX_CAPABILITIES: Final[None] = None  # stub constant
RESTRICTED_CAPABILITIES: Final[None] = None  # stub constant


def verify_capability_scope(*args, **kwargs):
    """Stub function — implementation pending."""
    raise NotImplementedError("verify_capability_scope not implemented")


__all__ = [
    "MAX_CAPABILITIES",
    "RESTRICTED_CAPABILITIES",
    "verify_capability_scope",
]
