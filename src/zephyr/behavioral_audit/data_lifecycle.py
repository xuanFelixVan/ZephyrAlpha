# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.data_lifecycle
# [DOMAIN] D-BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
# [A_module] module_id=MOD-SEC_data_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from __future__ import annotations

from enum import Enum


class DataStage(str, Enum):
    CREATE = "Create"
    STORE = "Store"
    USE = "Use"
    ARCHIVE = "Archive"
    PURGE = "Purge"


ARCHIVE_AFTER_YEARS: int = 7
PURGE_AFTER_YEARS: int = 15
GDPR_PII_FIELDS: list[str] = ["user", "payment", "email"]


def forget_pii() -> dict[str, str]:
    return {"action": "permanent_delete", "cert": "provided"}
