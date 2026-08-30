# [A_module] module_id=MOD-GOV-invariants | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, PostDocReviewScanner
#   code: __init__.py import L32
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 en_001_circular_dependency, en_002_enforcement_validator, en_003_contract_c…
#   desc: __init__ import L32；__all__ 6 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（6 符号）
#   name_en: __all__
#   intro: en_001_circular_dependency, en_002_enforcement_validator, en_003_contract_compa…
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.gov_enforcement.rule_enforcement.invariants.post_doc_review_check import PostDocReviewScanner

# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.invariants
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent

"""ZephyrAlpha — Architectural Invariant Gates (EN-001 ~ EN-003)

P0 结构不变量门禁（非 task-based，与 G0-G7 互补）：
  - EN-001: 循环依赖扫描器（topological sort on layer import graph）
  - EN-002: 强制模式 validator（contract enforcement 声明校验）
  - EN-003: 契约兼容性检查器（dataclass field ↔ contract spec diff）
"""

__all__ = [
    "en_001_circular_dependency",
    "en_002_enforcement_validator",
    "en_003_contract_compatibility",
    "en_process_lifecycle_gateway",
    "zero_residue_check",
    "post_doc_review_check",
]

__all__.append("PostDocReviewScanner")
