# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.compliance_gate_a6
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""D_COMPLIANCE — Compliance Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultSecurityGateway : SecurityGateway 的具体实现（正则检测 + 审计决策）
"""

from typing import Final

__all__: Final = ["compliance_manager", "compliance_mapper"]
