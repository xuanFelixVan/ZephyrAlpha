# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md
# [MODULE] zephyr.governance.ops_governance.ops_foundation
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
#   name: last_good 参数
#   fields: 参数 last_good，类型注解 str
#   code: ops_foundation.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: current 参数
#   fields: 参数 current，类型注解 str
#   code: ops_foundation.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① verify_config
#   name_en: verify_config
#   intro: verify_config(last_good, current) 源码 L82-L83
#   desc: 源码 L82-L83
#   inputs: last_good current
#   outputs: tuple[bool, str]
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[bool, str]
#   name_en: tuple[bool, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-020;MOD-INF-018;MOD-INF-027
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

from enum import Enum
from typing import Final


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
