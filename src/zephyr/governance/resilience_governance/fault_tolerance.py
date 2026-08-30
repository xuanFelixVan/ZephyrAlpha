# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.fault_tolerance
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.governance.resilience_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: fault_tolerance.py
# 层: 算法
# - id: A1
#   name_zh: ① RetryPolicy
#   name_en: RetryPolicy
#   intro: class RetryPolicy 源码 L102-L114
#   desc: 公共方法（定义序）: backoff, should_retry；源码 L102-L114
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② FaultToleranceManager
#   name_en: FaultToleranceManager
#   intro: class FaultToleranceManager 源码 L117-L131
#   desc: 公共方法（定义序）: degrade, is_fully_operational；源码 L117-L131
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: RetryPolicy, FaultToleranceManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Final


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
