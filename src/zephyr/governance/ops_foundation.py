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
