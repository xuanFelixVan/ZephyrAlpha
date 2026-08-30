# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.security.security_decision
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] l10-compliance ; llm-security.protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] enum members are frozen; no additions without ADR
# [MODIFY-GUARD] member changes require cross-package impact review
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] tests/test_shared_contracts_security.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: security_decision.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: SecurityDecision
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: SecurityDecision
#   downstream: l10-compliance ; llm-security.protocol
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from enum import Enum


class SecurityDecision(Enum):
    BLOCK = "block"
    ALLOW = "allow"
    DENY = "deny"
    FLAG = "flag"
