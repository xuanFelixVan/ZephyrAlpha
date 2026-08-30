# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.time_sync
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
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
#   code: time_sync.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: TimeSource
#   desc: 数据契约/异常/枚举声明共 1 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（1 类）
#   name_en: data classes
#   intro: TimeSource
#   downstream: MOD-INF-020;MOD-INF-018;MOD-INF-027
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

NTP_SERVER: Final[str] = "pool.ntp.org"
NTP_SYNC_INTERVAL_SECONDS: Final[int] = 60
MAX_CLOCK_DRIFT_MS: Final[int] = 50
TIMESTAMP_FORMAT: Final[str] = "ISO8601"


@dataclass(frozen=True)
class TimeSource:
    level: int
    name: str
    max_jitter_ms: int


TIME_HIERARCHY: Final[list[TimeSource]] = [
    TimeSource(1, "硬件NTP pool.ntp.org", 10),
    TimeSource(2, "系统时间 w32tm/timedatectl", 50),
    TimeSource(3, "业务应用BusinessTs UTC+8 1ms", 1),
]
