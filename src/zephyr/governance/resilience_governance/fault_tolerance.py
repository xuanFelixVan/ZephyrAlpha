# [BLUEPRINT] SRC-070 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.fault_tolerance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.resilience_governance.__init__
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
# [A_module] module_id=MOD-GOV_fault_tolerance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import random
from enum import Enum


class BulkheadPool(str, Enum):
    SIGNAL = "Signal"
    EXECUTION = "Execution"
    RESEARCH = "Research"
    SYSTEM = "System"


BULKHEAD_ALLOCATION: Final[dict[BulkheadPool, float]] = {
    BulkheadPool.SIGNAL: 0.30,
    BulkheadPool.EXECUTION: 0.25,
    BulkheadPool.RESEARCH: 0.25,
    BulkheadPool.SYSTEM: 0.20,
}

RETRY_BACKOFF_SEQUENCE: Final[list[float]] = [0.01, 0.1, 1.0, 10.0, 30.0]
MAX_RETRIES: Final[int] = 5
JITTER_RATIO: Final[float] = 0.25

E2E_TIMEOUT_MS: Final[int] = 460


class DegradationLevel(int, Enum):
    T0 = 0
    T1 = 1
    T2 = 2
    T3 = 3
    T4 = 4


DEGRADATION_LAYERS: Final[dict[DegradationLevel, str]] = {
    DegradationLevel.T0: "全功能——正常运作",
    DegradationLevel.T1: "信号更新 1min->5min (CPU>80%)",
    DegradationLevel.T2: "仅用核心因子 (数据源异常)",
    DegradationLevel.T3: "暂停执行只 Hold 现有仓位 (Broker不可达)",
    DegradationLevel.T4: "全系统logging不动任何指令 (行情+信号都不可用)",
}


class RetryPolicy:
    def __init__(self) -> None:
        self.sequence = list(RETRY_BACKOFF_SEQUENCE)
        self.max_retries = MAX_RETRIES
        self.jitter = JITTER_RATIO

    def backoff(self, attempt: int) -> float:
        base = self.sequence[min(attempt, len(self.sequence) - 1)]
        jitter_amount = random.uniform(-self.jitter, self.jitter) * base
        return max(0.001, base + jitter_amount)

    def should_retry(self, attempt: int) -> bool:
        return attempt < self.max_retries


class FaultToleranceManager:
    def __init__(self) -> None:
        self.degradation_level: DegradationLevel = DegradationLevel.T0
        self.retry_policy = RetryPolicy()

    def degrade(self, reason: str) -> DegradationLevel:
        levels = list(DegradationLevel)
        idx = self.degradation_level.value
        if idx + 1 < len(levels):
            self.degradation_level = levels[idx + 1]
        return self.degradation_level

    @property
    def is_fully_operational(self) -> bool:
        return self.degradation_level == DegradationLevel.T0
