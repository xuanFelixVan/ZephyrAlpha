# [BLUEPRINT] SRC-059 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.ops_foundation
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] zephyr.governance.ops_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ops_foundation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

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


OPS_BACKUPS: dict[BackupLayer, str] = {b: b.value for b in BackupLayer}
OPS_LOG_CATEGORIES: dict[LogCategory, str] = {l: l.value for l in LogCategory}

CONFIG_DRIFT_CHECK_PERIOD_HOURS: int = 24
LOG_SIZE_LIMIT_MB_PER_MODULE: int = 100
FREEZE_FILE = "freeze.txt"


def verify_config(last_good: str, current: str) -> tuple[bool, str]:
    return (last_good == current, "OK" if last_good == current else "DRIFT DETECTED")
