# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.daily_ops
# [DOMAIN] D_GOV_OPS_RESILIENCE
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
#   code: daily_ops.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: OpsPhase, QuickCommand
#   desc: 数据契约/异常/枚举声明共 2 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（2 类）
#   name_en: data classes
#   intro: OpsPhase, QuickCommand
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


class OpsPhase(str, Enum):
    P1_PRE_OPEN = "08:00-09:30 盘前"
    P2_CORE = "09:30-16:00 主交易"
    P3_CLOSE = "16:00-16:30 收市核实"
    P4_MAINTENANCE = "16:30-17:30 盘后维护"
    P5_SUMMARY = "17:30-18:00 日终总结"


class QuickCommand(str, Enum):
    CRISIS = "/crisis"
    STATUS = "/status"
    NOTES = "/notes"
    PUBLISH = "/publish"


QUICK_COMMANDS: Final[dict[QuickCommand, str]] = {
    QuickCommand.CRISIS: "立即Pause所有策略仅Emergency defense·内存Only",
    QuickCommand.STATUS: "实时关键指标clean dashboard",
    QuickCommand.NOTES: "所有今天关键事件->markdown->daily_notes.md",
    QuickCommand.PUBLISH: "将今天稳定变更发布到MOD-MASTER-001+bump版本号",
}
