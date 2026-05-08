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
