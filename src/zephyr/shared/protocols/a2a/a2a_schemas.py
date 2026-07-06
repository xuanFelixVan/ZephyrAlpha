# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_domain-shared/protocols/blueprint.md
# [MODULE] zephyr.shared.protocols.a2a.a2a_schemas
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.shared.protocols.a2a; zephyr.infrastructure.a2a_protocol
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] no imports from zephyr.infrastructure or zephyr.trading; data contracts only
# [MODIFY-GUARD] schema changes require consumer audit
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Pydantic validation errors on schema violation
# [TESTS] tests/test_shared_protocols.py
# [A_module] module_id=MOD-SHR_a2a_schemas | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A data structure contracts — Message, Task, and StateMachine schemas.

Pydantic models and enums that define the wire format for A2A communication.
These are data contracts shared between all domains.
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
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
