# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.ops_foundation
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
# [A_module] module_id=MOD-RES_ops_foundation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum


class BackupLayer(str, Enum):
    GIT = "Git"
    CLOUD_ZIP = "CloudZipDaily"
    DB_DUMP = "DbDumpTwice"
    SECRETS_VAULT = "SecretsVault"


class LogCategory(str, Enum):
    SYSTEM = "System"
    ORDER = "Order"
    MARKET = "Market"
    AI_DECISION = "AI_Decision"


OPS_BACKUPS: Final[dict[BackupLayer, str]] = {b: b.value for b in BackupLayer}
OPS_LOG_CATEGORIES: Final[dict[LogCategory, str]] = {l: l.value for l in LogCategory}

CONFIG_DRIFT_CHECK_PERIOD_HOURS: Final[int] = 24
LOG_SIZE_LIMIT_MB_PER_MODULE: Final[int] = 100
FREEZE_FILE: Final[str] = "freeze.txt"


def verify_config(last_good: str, current: str) -> tuple[bool, str]:
    return (last_good == current, "OK" if last_good == current else "DRIFT DETECTED")
