# [A_module] module_id=MOD-SEC-security_contracts_security | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.contracts.security
# [INVARIANTS] SecurityDecision enum values are frozen; no additions without ADR
# [MODIFY-GUARD] enum member changes require cross-package impact review
# [CONSUMERS] infrastructure_runtime_integration; l10-compliance; llm-security
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] tests/test_shared_contracts_security.py
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: SecurityDecision
#   code: __init__.py import L49
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 SecurityDecision, security_decision（共 2 符号）
#   desc: __init__ import L49；__all__ 2 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（2 符号）
#   name_en: __all__
#   intro: SecurityDecision, security_decision
#   downstream: infrastructure_runtime_integration; l10-compliance; llm-security
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = [
    "SecurityDecision",
    "security_decision",
]

from zephyr.shared.contracts.security.security_decision import SecurityDecision
