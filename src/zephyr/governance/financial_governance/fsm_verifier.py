# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.financial_governance.fsm_verifier
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.financial_governance.__init__
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
#   name: spec 参数
#   fields: 参数 spec，类型注解 FSMSpec
#   code: fsm_verifier.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: local_state 参数
#   fields: 参数 local_state，类型注解 FSMState
#   code: fsm_verifier.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: broker_state 参数
#   fields: 参数 broker_state，类型注解 FSMState
#   code: fsm_verifier.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① generate_test_cases
#   name_en: generate_test_cases
#   intro: generate_test_cases(spec) 源码 L142-L149
#   desc: 源码 L142-L149
#   inputs: spec
#   outputs: dict[str, list[str]]
# - id: A2
#   name_zh: ② reconcile_state
#   name_en: reconcile_state
#   intro: reconcile_state(local_state, broker_state) 源码 L152-L155
#   desc: 源码 L152-L155
#   inputs: local_state broker_state
#   outputs: tuple[FSMState, str]
#   （注：A2 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: dict[str, list[str]]
#   name_en: dict[str, list[str]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: tuple[FSMState, str]
#   name_en: tuple[FSMState, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Final

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FSMState(str, Enum):
    PENDING = "PENDING"
    ACK = "ACK"
    PARTIAL_FILL = "PARTIAL_FILL"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


FSM_INITIAL: Final[FSMState] = FSMState.PENDING
FSM_TERMINAL: Final[set[FSMState]] = {FSMState.FILLED, FSMState.REJECTED, FSMState.CANCELLED}


class FSMTransition(BaseModel):
    from_state: FSMState
    event: str
    to_state: FSMState


FSM_TRANSITIONS: Final[list[FSMTransition]] = [
    FSMTransition(from_state=FSMState.PENDING, event="ack_received", to_state=FSMState.ACK),
    FSMTransition(from_state=FSMState.ACK, event="partial_fill", to_state=FSMState.PARTIAL_FILL),
    FSMTransition(from_state=FSMState.PARTIAL_FILL, event="fill", to_state=FSMState.FILLED),
    FSMTransition(from_state=FSMState.ACK, event="fill", to_state=FSMState.FILLED),
    FSMTransition(from_state=FSMState.PENDING, event="reject", to_state=FSMState.REJECTED),
    FSMTransition(from_state=FSMState.ACK, event="cancel", to_state=FSMState.CANCELLED),
    FSMTransition(from_state=FSMState.PARTIAL_FILL, event="cancel", to_state=FSMState.CANCELLED),
]

FSM_INVARIANTS: Final[list[str]] = [
    "max one transition per event",
    "no transition from terminal states",
    "order_id unique across all live states",
]


class FSMInstance(BaseModel):
    entity_id: str
    current_state: FSMState = FSMState.PENDING

    def apply(self, event: str) -> bool:
        if self.current_state in FSM_TERMINAL:
            logger.warning("FSM %s: no transition from terminal %s", self.entity_id, self.current_state.value)
            return False
        for t in FSM_TRANSITIONS:
            if t.from_state == self.current_state and t.event == event:
                self.current_state = t.to_state
                return True
        return False


class FSMSpec(BaseModel):
    states: list[FSMState] = Field(default_factory=lambda: list(FSMState))
    initial: FSMState = FSMState.PENDING
    terminal: list[FSMState] = Field(default_factory=lambda: list(FSM_TERMINAL))
    transitions: list[FSMTransition] = Field(default_factory=lambda: list(FSM_TRANSITIONS))
    invariants: list[str] = Field(default_factory=lambda: list(FSM_INVARIANTS))


def generate_test_cases(spec: FSMSpec) -> dict[str, list[str]]:
    valid_tests: list[str] = []
    invalid_tests: list[str] = []
    for t in spec.transitions:
        valid_tests.append(f"test_CAN_{t.from_state.value}_{t.event}_{t.to_state.value}")
    for state in spec.terminal:
        invalid_tests.append(f"test_CANNOT_{state.value}_any_transition")
    return {"valid": valid_tests, "invalid": invalid_tests}


def reconcile_state(local_state: FSMState, broker_state: FSMState) -> tuple[FSMState, str]:
    if local_state == broker_state:
        return local_state, "consistent — recover"
    return broker_state, "broker is source of truth — incident logged"
