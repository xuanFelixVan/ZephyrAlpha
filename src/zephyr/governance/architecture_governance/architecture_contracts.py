# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.architecture_contracts
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
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
#   code: architecture_contracts.py
# 层: 算法
# - id: A1
#   name_zh: ① CircuitBreaker
#   name_en: CircuitBreaker
#   intro: class CircuitBreaker 源码 L102-L141
#   desc: 公共方法（定义序）: failure_count, state, record_failure, record_success, attempt_reset；源码 L102-L141
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② generate_client_order_id
#   name_en: generate_client_order_id
#   intro: generate_client_order_id() 源码 L144-L145
#   desc: 源码 L144-L145
#   inputs: 无参数
#   outputs: str
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Final

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
        description="同步 Critical 信号->风控 <10ms· 异步 非关键 ≥50ms",
    ),
    "C3_IDEMPOTENCY": Contract(
        name="幂等性保证",
        description="订单幂等 key={client_order_id: uuid4V4, timestamp: int64}· 信号幂等 key={signal_id + tick_ts_ms}",
    ),
    "C4_CIRCUIT_BREAKER": Contract(
        name="断路器",
        description="Closed->failures>5/60s->OPEN(1min)->Half-Open->成功->Closed/失败->OPEN",
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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def failure_count(self) -> int:
        """只读：failure_count（Stage 4 公共化）。"""
        return self._failure_count

    @failure_count.setter
    def failure_count(self, value):
        """写入：failure_count（Stage 4 公共化）。"""
        self._failure_count = value

    @property
    def state(self) -> CircuitBreakerState:
        return self._state

    @state.setter
    def state(self, value):
        """写入：state（Stage 4 公共化）。"""
        self._state = value

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
