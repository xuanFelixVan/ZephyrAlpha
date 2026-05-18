# [BLUEPRINT] MOD-INF-023 | docs/03_modules/l01_infrastructure/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_auditor.data_lifecycle
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/drift-detector/blueprint.md;src/zephyr/behavioral_auditor/__init__.py
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/
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
