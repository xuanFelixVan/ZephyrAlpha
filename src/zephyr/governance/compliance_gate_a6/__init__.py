# [A_module] module_id=MOD-GOV_compliance_gate_a6 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain-compliance/compliance-core/blueprint.md
# [MODULE] zephyr.governance.implementations
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""L10 — Compliance Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultSecurityGateway : SecurityGateway 的具体实现（正则检测 + 审计决策）
"""

# MIGRATED: from zephyr.governance.implementations.default_security_gateway import (  # removed by TC-7-2
# DefaultSecurityGateway,  # removed by TC-7-2
# )  # removed by TC-7-2
#
# __all__ = ['DefaultSecurityGateway', 'default_security_gateway']
#

__all__ = [
    "default_security_gateway",
]
