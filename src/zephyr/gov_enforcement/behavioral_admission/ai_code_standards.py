# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ai_code_standards.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: ai_code_standards.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L63；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.gov_enforcement.behavioral_admission.ai_code_standards
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV-ai_code_standards | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

CODE_CONVENTIONS: Final[dict[str, str]] = {
    "file_org": "按YAML约定abord",
    "scaffold": "python setup+page=模板自动生成",
    "header": "Python: shebang+path",
    "comments": "no justification/no redundant->code self-document->majors only",
    "imports": "future->stdlib->3rd->local+isort",
    "type_hints": "全部public函数must",
}

AI_FORBIDDEN: Final[list[str]] = [
    "禁止生成注释in demo/example",
    "测试必须Fail(TDD mode)->pass=bad",
]
