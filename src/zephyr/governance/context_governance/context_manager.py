# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md;src/zephyr/governance/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: TokenTier, HallucinationLevel
#   desc: 数据契约/异常/枚举声明共 2 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: TokenTier, HallucinationLevel
#   downstream: MOD-INF-020;MOD-INF-018;MOD-INF-027
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final


class TokenTier(str, Enum):
    T0 = "T0_500"
    T1 = "T1_2K"
    T2 = "T2_5K"
    T3 = "T3_18K"
    T4 = "T4_40K"


TIER_TOKENS: Final[dict[TokenTier, int]] = {
    TokenTier.T0: 500,
    TokenTier.T1: 2000,
    TokenTier.T2: 5000,
    TokenTier.T3: 18000,
    TokenTier.T4: 40000,
}


class HallucinationLevel(str, Enum):
    L1_FACT = "L1_fact_inconsistency"
    L2_BLUEPRINT = "L2_blueprint_conflict"
    L3_SELF_REF = "L3_self_refuting"


TRIM_DUPLICATE_THRESHOLD: Final[float] = 0.30
MAX_HISTORY_DAYS: Final[int] = 30
