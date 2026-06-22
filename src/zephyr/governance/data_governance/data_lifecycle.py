# [A_module] module_id=MOD-GOV_data_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-031 | docs/03_modules/_domain-governance/blueprint.md | §

# [MODULE] zephyr.governance.data_lifecycle

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
