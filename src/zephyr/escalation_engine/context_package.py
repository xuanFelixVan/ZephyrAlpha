# [BLUEPRINT] MOD-INF-022 | 03_modules/l01_infrastructure/escalation-protocol/blueprint.md | §

# [MODULE] zephyr.escalation_engine.context_package

# [INVARIANTS] 7字段结构不可变;context_snapshot必须完整

# [MODIFY-GUARD] docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md

# [CONSUMERS] zephyr.escalation_engine.delegation_engine;zephyr.escalation_engine.delegation_manager

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id

# [TESTS] tests/test_escalation_engine.py

"""

Context Package — D-022-08 委托上下文包: 升级原因+证据链+历史try_trace。
"""
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
