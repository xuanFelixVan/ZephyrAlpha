from __future__ import annotations
from enum import Enum

class TIFLevel(str, Enum):
    L1 = "L1_<5m"
    L2 = "L2_5-30m"
    L3 = "L3_30m-4h"
    L4 = "L4_4-24h"
    L5 = "L5_24h+"

DECAY_START_HOURS: int = 8
DECAY_RATE_PER_24H: float = 0.25
MAX_DECAY_HOURS: int = 72

E2E_TARGET_MS: int = 460
E2E_BUDGET_BREAKDOWN_MS: dict[str, int] = {
    "MARKETDATA": 405, "SIGNAL": 1000, "RISK": 50,
}
