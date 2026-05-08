"""Context Package — D-022-08 委托上下文包: 升级原因+证据链+历史try_trace。"""
from __future__ import annotations
from pydantic import BaseModel,Field
from datetime import datetime,timezone

class EscalationContext(BaseModel):
    context_id:str
    task_id:str=""
    reason:str=""
    evidence_chain:list[str]=Field(default_factory=list)
    try_trace:list[dict]=Field(default_factory=list)
    escalated_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
    escalation_level:str=""
    suggested_action:str=""

class ContextPackageBuilder:
    def build(self, task_id:str, reason:str, level:str, evidence:list[str]=None,trace:list[dict]=None)->EscalationContext:
        return EscalationContext(
            context_id=f"CTX-{task_id}",
            task_id=task_id,
            reason=reason,
            escalation_level=level,
            evidence_chain=evidence or [],
            try_trace=trace or [],
        )
