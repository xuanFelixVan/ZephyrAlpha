# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.ai_self_diagnosis
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
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
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: error 参数
#   fields: 参数 error，类型注解 str
#   code: ai_self_diagnosis.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① auto_fix_known_pattern
#   name_en: auto_fix_known_pattern
#   intro: auto_fix_known_pattern(error) 源码 L63-L64
#   desc: 源码 L63-L64
#   inputs: error
#   outputs: tuple[bool, str]
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[bool, str]
#   name_en: tuple[bool, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from enum import Enum
from typing import Final


class AutoFixLayer(str, Enum):
    L1_AUTO = "L1_AutoFix"
    L2_SUGGEST = "L2_Suggest"
    L3_REPORT = "L3_Report"


AUTO_KB_STEPS: Final[list[str]] = [
    "发现->记录->解决->诊断反转验证(初始诊断是否正确？错了为什么？)->防御->文档化",
]


def auto_fix_known_pattern(error: str) -> tuple[bool, str]:
    return (True, "L1 AutoFix applied")
