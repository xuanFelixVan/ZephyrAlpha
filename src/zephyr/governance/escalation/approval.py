"""G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请求数据结构."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    task_id: str
    requested_action: str
    human_approver: str
    reason: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    priority: str = "P2"
    status: str = "PENDING"
