"""G-CT-008 — A2ACommunication Pydantic V2 BaseModel agent-to-agent 通信数据结构."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    QUERY = "QUERY"
    COMMAND = "COMMAND"
    NOTIFY = "NOTIFY"
    DELEGATE = "DELEGATE"
    RESPONSE = "RESPONSE"


class A2ACommunication(BaseModel):
    a2a_id: str
    from_agent_id: str
    to_agent_id: str
    message_type: MessageType = MessageType.QUERY
    payload_size: int = 0
    transfer_token_count: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "PENDING"
