# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_package
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.intelligence_governance.delegation_engine;zephyr.governance.intelligence_governance.delegation_manager
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 7字段结构不可变;context_snapshot必须完整
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_context_package | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Context Package — D-022-08 委托上下文包: 升级原因+证据链+历史try_trace。
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class EscalationContext(BaseModel):
    context_id: str
    task_id: str = ""
    reason: str = ""
    evidence_chain: list[str] = Field(default_factory=list)
    try_trace: list[dict] = Field(default_factory=list)
    escalated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    escalation_level: str = ""
    suggested_action: str = ""


class ContextPackageBuilder:
    def build(
        self, task_id: str, reason: str, level: str, evidence: list[str] = None, trace: list[dict] = None
    ) -> EscalationContext:
        return EscalationContext(
            context_id=f"CTX-{task_id}",
            task_id=task_id,
            reason=reason,
            escalation_level=level,
            evidence_chain=evidence or [],
            try_trace=trace or [],
        )


class ContextPackage:
    def __init__(self, package_id="", source="", target="", context_type="", payload=None, timestamp=None):
        self.package_id = package_id
        self.source = source
        self.target = target
        self.context_type = context_type
        self.payload = payload or {}
        self.timestamp = timestamp
