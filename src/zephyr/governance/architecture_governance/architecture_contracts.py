# [BLUEPRINT] SRC-011 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.architecture_contracts
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
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
# [A_module] module_id=MOD-GOV_architecture_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import uuid
from enum import Enum

from pydantic import BaseModel


class CircuitBreakerState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class Contract(BaseModel):
    name: str
    description: str
    status: str = "active"


ARCH_BASE_CONTRACTS: Final[dict[str, Contract]] = {
    "C1_COMMUNICATION": Contract(
        name="模块间通信",
        description="数据格式 JSON（跨模块）· 版本管理 v1/get_signal· 契约存档 CT-### in MOD-MASTER_BLUEPRINT",
    ),
    "C2_SYNC_ASYNC": Contract(
        name="同步/异步边界",
        description="同步 Critical 信号→风控 <10ms· 异步 非关键 ≥50ms",
    ),
    "C3_IDEMPOTENCY": Contract(
        name="幂等性保证",
        description="订单幂等 key={client_order_id: uuid4V4, timestamp: int64}· 信号幂等 key={signal_id + tick_ts_ms}",
    ),
    "C4_CIRCUIT_BREAKER": Contract(
        name="断路器",
        description="Closed→failures>5/60s→OPEN(1min)→Half-Open→成功→Closed/失败→OPEN",
    ),
    "C5_LAMPORT": Contract(
        name="最终一致性 Lamport",
        description="Lamport happened_before 跨模块事件顺序",
    ),
}


class CircuitBreaker:
    def __init__(self) -> None:
        self._state = CircuitBreakerState.CLOSED
        self._failure_count: int = 0
        self._threshold: int = 5
        self._window_seconds: int = 60

    @property
    def state(self) -> CircuitBreakerState:
        return self._state

    def record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self._threshold and self._state is CircuitBreakerState.CLOSED:
            self._state = CircuitBreakerState.OPEN

    def record_success(self) -> None:
        if self._state is CircuitBreakerState.HALF_OPEN:
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0

    def attempt_reset(self) -> None:
        if self._state is CircuitBreakerState.OPEN:
            self._state = CircuitBreakerState.HALF_OPEN


def generate_client_order_id() -> str:
    return f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:8]}"
