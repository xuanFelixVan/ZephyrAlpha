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
"""
D_COMPLIANCE — Compliance Concrete Implementations

Phase C 具体实现包。

实现清单：
  - DefaultSecurityGateway : SecurityGateway 的具体实现（正则检测 + 审计决策）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: Final
#   code: __init__.py import L48
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 Final（共 1 符号）
#   desc: __init__ import L48；__all__ 0 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（1 符号）
#   name_en: __all__
#   intro: Final
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

__all__: Final = ["compliance_manager", "compliance_mapper"]
