# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_state

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A Task 状态机 — Layer 2 Communication"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


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
    to_agent: Optional[str] = None
    description: str
    context_ref: Optional[str] = None
    context_package: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
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
            task.updated_at = datetime.utcnow()
            return True
        return False
