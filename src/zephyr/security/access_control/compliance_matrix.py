# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.security.access_control.compliance_matrix
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Stub module: zephyr.security.access_control.compliance_matrix — implementation pending."""

from typing import Final

COMPLIANCE_MATRIX: Final[None] = None  # stub constant


class ComplianceItem:
    """Stub class — implementation pending."""

    pass


class ComplianceStatus:
    """Stub class — implementation pending."""

    pass


def compliant_items(*args, **kwargs):
    """Stub function — implementation pending."""
    raise NotImplementedError("compliant_items not implemented")


def get_by_reg_id(*args, **kwargs):
    """Stub function — implementation pending."""
    raise NotImplementedError("get_by_reg_id not implemented")


def non_compliant_items(*args, **kwargs):
    """Stub function — implementation pending."""
    raise NotImplementedError("non_compliant_items not implemented")


__all__ = [
    "COMPLIANCE_MATRIX",
    "ComplianceItem",
    "ComplianceStatus",
    "compliant_items",
    "get_by_reg_id",
    "non_compliant_items",
]
