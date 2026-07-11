# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.daily_ops
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-RES_daily_ops | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum


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
