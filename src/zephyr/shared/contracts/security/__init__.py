# [A_module] module_id=MOD-SEC-security_contracts_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.contracts.security
# [DOMAIN] D_INFRA_OPS
# [INVARIANTS] SecurityDecision enum values are frozen; no additions without ADR
# [MODIFY-GUARD] enum member changes require cross-package impact review
# [CONSUMERS] infrastructure_runtime_integration; l10-compliance; llm-security
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] none  # 2026-09-05 AI-00：全仓无测试 import 本模块（原声明路径不存在）
# [TTL] permanent

"""


# [ALGO_FLOW] external: docs/03_modules/_domain_shared/algo_flow/contracts/security/security__init__.yaml
"""

__all__ = [
    "SecurityDecision",
    "security_decision",
]

from zephyr.shared.contracts.security.security_decision import SecurityDecision
