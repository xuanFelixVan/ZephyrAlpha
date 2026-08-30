# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.gov_enforcement.behavioral_admission.code_review_ai
# [DOMAIN] D_GOV_ENFORCEMENT
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
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: code_review_ai.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: ReviewLevel
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: ReviewLevel
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final


# class-name-alias: migrated from governance/behavioral_admission; pre-existing same-name class in trading/integration (ARCH-034 debt, to be resolved in dedicated cleanup)
class ReviewLevel(str, Enum):
    L0_RUFF = "L0_ruff"
    L1_SECURITY = "L1_security"
    L2_LOGIC = "L2_logic"
    L3_ARCH = "L3_arch"
    L4_STRATEGY = "L4_strategy"
    L5_DUAL_AI = "L5_dual_ai"


REVIEW_TIMEOUTS: Final[dict[ReviewLevel, int]] = {
    ReviewLevel.L0_RUFF: 1,
    ReviewLevel.L1_SECURITY: 5,
    ReviewLevel.L2_LOGIC: 5,
    ReviewLevel.L3_ARCH: 30,
    ReviewLevel.L4_STRATEGY: 60,
    ReviewLevel.L5_DUAL_AI: 120,
}

REVIEW_RULES: Final[list[str]] = [
    "所有AI产出MUST通过L3",
    "模块部署前L3+L4完整审查",
    "黄金路径: AI自L2->AI同伴L3->Owner L4标志->终",
]
