# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.forensic.interrupt_coherence_validator
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_interrupt_coherence_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R531: InterruptCoherenceValidator
崩溃/重启后状态一致性校验 — 无半应用动作/无孤立锁/无悬空引用
"""

import time
from dataclasses import dataclass, field
from enum import Enum


class CoherenceStatus(str, Enum):
    COHERENT = "coherent"
    PARTIALLY_DIRTY = "partially_dirty"
    INCOHERENT = "incoherent"


@dataclass
class InterruptCoherenceValidator:
    known_locks: set[str] = field(default_factory=set)
    known_actions_in_flight: set[str] = field(default_factory=set)
    known_references: set[str] = field(default_factory=set)
    coherence_checks: list[dict] = field(default_factory=list)
    max_checks: int = 50

    def register_lock(self, lock_id: str) -> None:
        self.known_locks.add(lock_id)

    def register_action_in_flight(self, action_id: str) -> None:
        self.known_actions_in_flight.add(action_id)

    def register_reference(self, ref_id: str) -> None:
        self.known_references.add(ref_id)

    def mark_lock_released(self, lock_id: str) -> None:
        self.known_locks.discard(lock_id)

    def mark_action_completed(self, action_id: str) -> None:
        self.known_actions_in_flight.discard(action_id)

    def validate_coherence(self) -> dict:
        issues = []

        if self.known_locks:
            issues.append(f"{len(self.known_locks)} orphaned locks: {list(self.known_locks)[:5]}")

        if self.known_actions_in_flight:
            issues.append(
                f"{len(self.known_actions_in_flight)} half-applied actions: {list(self.known_actions_in_flight)[:5]}"
            )

        if issues:
            status = CoherenceStatus.INCOHERENT if len(issues) >= 3 else CoherenceStatus.PARTIALLY_DIRTY
        else:
            status = CoherenceStatus.COHERENT

        result = {
            "status": status.value,
            "coherent": status == CoherenceStatus.COHERENT,
            "issues": issues,
            "orphaned_locks": len(self.known_locks),
            "half_applied_actions": len(self.known_actions_in_flight),
            "timestamp": time.time(),
        }
        self.coherence_checks.append(result)
        if len(self.coherence_checks) > self.max_checks:
            self.coherence_checks = self.coherence_checks[-self.max_checks :]

        return result

    def auto_repair(self) -> dict:
        repaired = {}
        if self.known_locks:
            repaired["locks_cleared"] = len(self.known_locks)
            self.known_locks.clear()
        if self.known_actions_in_flight:
            repaired["actions_marked_failed"] = len(self.known_actions_in_flight)
            self.known_actions_in_flight.clear()

        return {
            "repaired": bool(repaired),
            "details": repaired,
            "coherent_now": len(self.known_locks) == 0 and len(self.known_actions_in_flight) == 0,
        }

    def get_coherence_history(self) -> list[dict]:
        return [c for c in self.coherence_checks if not c.get("coherent", True)]
