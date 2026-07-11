# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.time_sync
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
# [A_module] module_id=MOD-RES_time_sync | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from dataclasses import dataclass

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
