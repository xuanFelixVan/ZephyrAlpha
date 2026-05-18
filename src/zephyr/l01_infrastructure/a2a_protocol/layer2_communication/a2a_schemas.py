# [BLUEPRINT] MOD-INF-025 | 03_modules/l01_infrastructure/a2a-protocol/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.a2a_protocol.layer2_communication.a2a_schemas

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""A2A Message/Part 系统 — Layer 2 Communication"""

from enum import Enum
from typing import Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field


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
    parts: List[A2AMessagePart] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    context_ref: Optional[str] = None

    def add_part(self, part_type: PartType, content: str, metadata: dict = None) -> A2AMessagePart:
        part = A2AMessagePart(part_type=part_type, content=content, metadata=metadata or {})
        self.parts.append(part)
        return part
