# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.decision_registry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""决策注册表——所有权限decision记录+可查询历史+统计分析."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class DecisionRecord(BaseModel):
    decision_id: str
    agent_id: str
    action: str
    resource: str
    result: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    latency_ms: float = 0.0
    blocked_layer: str = ""
    rule_id: str = ""


class DecisionRegistry:
    _MAX_RECORDS: int = 10000

    def __init__(self) -> None:
        self._decisions: list[DecisionRecord] = []

    def log(self, agent_id: str, action: str, resource: str, result: str, blocked_layer: str = "", rule_id: str = "", latency_ms: float = 0.0) -> DecisionRecord:
        import secrets

        record = DecisionRecord(
            decision_id=f"DEC-{secrets.token_hex(6)}",
            agent_id=agent_id,
            action=action,
            resource=resource,
            result=result,
            latency_ms=latency_ms,
            blocked_layer=blocked_layer,
            rule_id=rule_id,
        )
        self._decisions.append(record)
        if len(self._decisions) > self._MAX_RECORDS:
            self._decisions = self._decisions[-self._MAX_RECORDS:]
        return record

    def query(self, agent_id: str = "", action: str = "") -> list[DecisionRecord]:
        results = self._decisions
        if agent_id:
            results = [r for r in results if r.agent_id == agent_id]
        if action:
            results = [r for r in results if r.action == action]
        return results

    def stats(self) -> dict[str, Any]:
        total = len(self._decisions)
        allowed = sum(1 for r in self._decisions if r.result == "ALLOWED")
        denied = sum(1 for r in self._decisions if r.result == "DENIED")
        avg_latency = sum(r.latency_ms for r in self._decisions) / max(total, 1)
        return {"total": total, "allowed": allowed, "denied": denied, "deny_rate": denied / max(total, 1), "avg_latency_ms": avg_latency}
