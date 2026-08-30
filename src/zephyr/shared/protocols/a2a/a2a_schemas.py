# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.a2a_schemas
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] no imports from zephyr.infrastructure or zephyr.trading; data contracts only
# [MODIFY-GUARD] schema changes require consumer audit
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Pydantic validation errors on schema violation
# [TESTS] tests/test_shared_protocols.py
# [A_module] module_id=MOD-SHARED-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
A2A data structure contracts — Message, Task, and StateMachine schemas.

Pydantic models and enums that define the wire format for A2A communication.
These are data contracts shared between all domains.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: task_id 参数
#   fields: 参数 task_id（无注解）
#   code: a2a_schemas.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: source_agent 参数
#   fields: 参数 source_agent（无注解）
#   code: a2a_schemas.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① A2AStateMachine
#   name_en: A2AStateMachine
#   intro: class A2AStateMachine 源码 L168-L185
#   desc: 公共方法（定义序）: transition；源码 L168-L185
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ContextPackage
#   name_en: ContextPackage
#   intro: class ContextPackage 源码 L188-L215
#   desc: 公共方法（定义序）: add_blueprint, add_decision, set_session_state, to_dict；源码 L188-L215
#   inputs: task_id source_agent
#   outputs: 返回值
# - id: A3
#   name_zh: ③ HandoffRecord
#   name_en: HandoffRecord
#   intro: class HandoffRecord 源码 L218-L235
#   desc: 公共方法（定义序）: to_dict；源码 L218-L235
#   inputs: from_agent to_agent task_id reason
#   outputs: 返回值
# - id: A4
#   name_zh: ④ HandoffManagerProtocol
#   name_en: HandoffManagerProtocol
#   intro: class HandoffManagerProtocol 源码 L239-L242
#   desc: 公共方法（定义序）: handoff, acknowledge；源码 L239-L242
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ MessageRouterProtocol
#   name_en: MessageRouterProtocol
#   intro: class MessageRouterProtocol 源码 L246-L249
#   desc: 公共方法（定义序）: register_handler, route；源码 L246-L249
#   inputs: 无参数
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ PushNotifierProtocol
#   name_en: PushNotifierProtocol
#   intro: class PushNotifierProtocol 源码 L253-L258
#   desc: 公共方法（定义序）: subscribe, unsubscribe, notify；源码 L253-L258
#   inputs: 无参数
#   outputs: 返回值
#   （注：A6 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（11 定义）
#   name_en: public defs
#   intro: A2AStateMachine, ContextPackage, HandoffRecord, HandoffManagerProtocol, Message…
#   downstream: zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from zephyr.shared.utils.time_utils import now_utc


class PartType(str, Enum):
    TEXT = "text"
    CODE = "code"
    FILE = "file"
    BLUEPRINT_REF = "blueprint_ref"
    GATE_RESULT = "gate_result"
    ERROR = "error"


class A2AMessagePart(BaseModel):
    part_type: PartType
    content: str
    metadata: dict = {}


class A2AMessage(BaseModel):
    message_id: str = Field(..., pattern=r"^a2a-msg-[a-z0-9-]+$")
    from_agent: str
    to_agent: str
    task_id: str
    parts: list[A2AMessagePart] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    context_ref: str | None = None

    def add_part(self, part_type: PartType, content: str, metadata: dict | None = None) -> A2AMessagePart:
        part = A2AMessagePart(part_type=part_type, content=content, metadata=metadata or {})
        self.parts.append(part)
        return part


class A2ATaskStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_REVIEW = "waiting_review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class A2ATask(BaseModel):
    task_id: str = Field(..., pattern=r"^a2a-task-[a-z0-9-]+$")
    status: A2ATaskStatus = A2ATaskStatus.CREATED
    from_agent: str
    to_agent: str | None = None
    description: str
    context_ref: str | None = None
    context_package: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)
    deadline: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    retry_count: int = 0
    max_retries: int = 3


class A2AStateMachine:
    VALID_TRANSITIONS = {
        A2ATaskStatus.CREATED: [A2ATaskStatus.QUEUED, A2ATaskStatus.CANCELLED],
        A2ATaskStatus.QUEUED: [A2ATaskStatus.ASSIGNED, A2ATaskStatus.CANCELLED, A2ATaskStatus.TIMEOUT],
        A2ATaskStatus.ASSIGNED: [A2ATaskStatus.IN_PROGRESS, A2ATaskStatus.CANCELLED],
        A2ATaskStatus.IN_PROGRESS: [A2ATaskStatus.WAITING_REVIEW, A2ATaskStatus.FAILED, A2ATaskStatus.CANCELLED],
        A2ATaskStatus.WAITING_REVIEW: [A2ATaskStatus.COMPLETED, A2ATaskStatus.FAILED],
        A2ATaskStatus.FAILED: [A2ATaskStatus.QUEUED],
    }

    @classmethod
    def transition(cls, task: A2ATask, new_status: A2ATaskStatus) -> bool:
        allowed = cls.VALID_TRANSITIONS.get(task.status, [])
        if new_status in allowed:
            task.status = new_status
            task.updated_at = now_utc()
            return True
        return False


class ContextPackage:
    def __init__(self, task_id: str, source_agent: str):
        self.task_id = task_id
        self.source_agent = source_agent
        self.created_at = now_utc()
        self.blueprints: dict[str, str] = {}
        self.decisions: list = []
        self.session_state: dict[str, Any] = {}
        self.locks_held: list = []

    def add_blueprint(self, name: str, content: str):
        self.blueprints[name] = content

    def add_decision(self, decision_id: str, data: dict[str, Any]):
        self.decisions.append({"id": decision_id, "data": data})

    def set_session_state(self, state: dict[str, Any]):
        self.session_state = state

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "source_agent": self.source_agent,
            "created_at": self.created_at.isoformat(),
            "blueprint_count": len(self.blueprints),
            "decision_count": len(self.decisions),
            "session_state_keys": list(self.session_state.keys()),
        }


class HandoffRecord:
    def __init__(self, from_agent: str, to_agent: str, task_id: str, reason: str):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.task_id = task_id
        self.reason = reason
        self.timestamp = now_utc()
        self.acknowledged = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_agent,
            "to": self.to_agent,
            "task_id": self.task_id,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
        }


@runtime_checkable
class HandoffManagerProtocol(Protocol):
    def handoff(self, from_agent: str, to_agent: str, task_id: str, reason: str) -> HandoffRecord: ...

    def acknowledge(self, to_agent: str, task_id: str) -> bool: ...


@runtime_checkable
class MessageRouterProtocol(Protocol):
    def register_handler(self, part_type: PartType, handler: Callable) -> None: ...

    def route(self, message: A2AMessage) -> dict[str, list]: ...


@runtime_checkable
class PushNotifierProtocol(Protocol):
    def subscribe(self, agent_id: str, callback: Callable) -> None: ...

    def unsubscribe(self, agent_id: str, callback: Callable) -> None: ...

    def notify(self, agent_id: str, event: str, data: dict | None = None) -> int: ...
