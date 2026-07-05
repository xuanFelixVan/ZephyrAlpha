# [BLUEPRINT] SRC-002 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.data_governance.data_lifecycle
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
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
# [A_module] module_id=MOD-DAT_data_lifecycle | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
