# [A_module] module_id=MOD-GOV-implementations | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.implementations
# [DOMAIN] D_SECURITY
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
D_COMPLIANCE — Compliance Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultSecurityGateway : SecurityGateway 的具体实现（正则检测 + 审计决策）

# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/implementations/implementations__init__.yaml
"""

from zephyr.governance.implementations.default_security_gateway import DefaultSecurityGateway

__all__ = [
    "DefaultSecurityGateway",
    "default_security_gateway",
]
# 2026-09-05 AI-00 审计：default_experiment_pipeline 治理版僵尸副本已退役（零 import 消费，
# 活体=src/zephyr/simulation/implementations/default_experiment_pipeline.py），沿 AI-AUDIT13-001 salvage 裁定
