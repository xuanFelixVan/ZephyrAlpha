# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.actors.owner_absence_escalation
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Owner Absence Escalation — v0.37.0 R462

Blindspot: Sole operator is offline/unresponsive; critical FLE decisions
wait indefinitely for human approval that never comes.

Risk: R462 — FLE deadlocked waiting for operator who is unavailable.

Mitigation: Tiered escalation with timeouts. Urgent actions auto-escalate
after configurable window. Non-urgent queue with max staleness.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class AbsenceState(str, Enum):
    PRESENT = "PRESENT"
    UNRESPONSIVE = "UNRESPONSIVE"
    ABSENT = "ABSENT"


@dataclass
class OwnerAbsenceEscalation:
    warning_timeout: float = 300.0
    critical_timeout: float = 900.0
    max_queue_age: float = 3600.0

    state: AbsenceState = AbsenceState.PRESENT
    last_ack: float = field(default_factory=time.time)
    pending_decisions: list[dict] = field(default_factory=list)
    auto_approved: int = 0

    def owner_ack(self) -> None:
        self.last_ack = time.time()  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
        self.state = AbsenceState.PRESENT

    def check_absence(self) -> AbsenceState:
        elapsed = time.time() - self.last_ack  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
        if elapsed > self.critical_timeout:
            self.state = AbsenceState.ABSENT
        elif elapsed > self.warning_timeout:
            self.state = AbsenceState.UNRESPONSIVE
        return self.state

    def submit_decision(self, decision_id: str, urgency: str) -> dict:
        self.pending_decisions.append(
            {
                "id": decision_id,
                "urgency": urgency,
                "submitted_at": time.time(),  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
            }
        )
        self._prune_stale()

        if self.check_absence() is AbsenceState.ABSENT and urgency == "critical":
            self.auto_approved += 1
            return {"decision": decision_id, "action": "auto_approved", "reason": "owner_absent"}

        return {"decision": decision_id, "action": "queued", "reason": "awaiting_owner"}

    def _prune_stale(self) -> None:
        cutoff = time.time() - self.max_queue_age  # noqa: m46-time  M46豁免: epoch秒浮点时间戳用于存活心跳与时效计算，非本地时区展示
        self.pending_decisions = [d for d in self.pending_decisions if d["submitted_at"] > cutoff]
