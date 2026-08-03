# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.ai_guards.ai_audit_guard
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditRecord:
    operation: str
    agent_id: str
    timestamp: float
    details: dict[str, Any] = field(default_factory=dict)
    approved: bool = True


class AiAuditGuard:
    def __init__(self, require_approval_for: tuple[str, ...] = ("delete", "modify_core")):
        self._require_approval = set(require_approval_for)
        self._records: list[AuditRecord] = []
        self._pending: list[AuditRecord] = []

    def check(self, operation: str, agent_id: str, **details: Any) -> AuditRecord:
        needs_approval = any(op in operation for op in self._require_approval)
        record = AuditRecord(
            operation=operation,
            agent_id=agent_id,
            timestamp=time.time(),
            details=details,
            approved=not needs_approval,
        )
        if needs_approval:
            self._pending.append(record)
        else:
            self._records.append(record)
        return record

    def approve(self, operation: str, agent_id: str) -> bool:
        for i, r in enumerate(self._pending):
            if r.operation == operation and r.agent_id == agent_id:
                r.approved = True
                self._records.append(r)
                self._pending.pop(i)
                return True
        return False

    def get_pending(self) -> list[AuditRecord]:
        return list(self._pending)
