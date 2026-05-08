from __future__ import annotations
from enum import Enum

class IntegrityDim(str, Enum):
    MARKET_COVERAGE = "MARKET_COVERAGE"
    FACTOR_CONSISTENCY = "FACTOR_CONSISTENCY"
    BACKTEST_STABILITY = "BACKTEST_STABILITY"
    HFT_FIDELITY = "HFT_FIDELITY"

PIT_MAX_DELAY_MINUTES: int = 15
HEALTH_CHECK_INTERVAL: dict[str, str] = {
    "monthly": "所有dim+grid自动run",
    "quarterly": "full2016-2024 re-run vs Sept→bias report",
}
